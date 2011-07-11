from Products.qi.util.lib.pyExcelerator import ImportXLS
from qi.sqladmin import models as DB
from Products.qi.datacapture.validation import validationrules
from Products.qi.util.logger import logger

from threading import Thread


import random
import os
import os.path
import datetime




class Upload:
    rows=[]
    def __init__(self):
        self.errors={}
    def buildrows(self, filename):                
        self.translator.loadData(filename)
        self.rows=self.translator.getRows()
    
    #does a python import to get the processing tool
    def doImport(self, reporttype):
        parts=reporttype.rsplit('.',1)
        module=__import__(parts[0])
        
        objname=parts[1]
        moduleparts=parts[0].split('.')[1:]
        for part in moduleparts:
            module=getattr(module, part)
        return getattr(module,objname)()

    def validateRows(self):
        rownum=1
        for row in self.rows:
            if not row:
                message='illegal empty row %i'%rownum
                self.addError('base',message)
            #unusual behavior, this validate returns a name if a problem
            #occured, and 'None' if there are no problems
            else: 
                result=row.validate()
                row.rownum=rownum
                if result:
                    #+1 because we skipped the first row
                    message='invalid value %s for on row %i'%(result,rownum+1)
                    self.addError('base',message)
            rownum+=1
        
        #don't return, implicit in hasErrors
        
    def getRequiredMeasures(self):
        measuresneeded={}
        for row in self.rows:
            if not measuresneeded.has_key(row.measure):
                measuresneeded[row.measure]='required'
        return measuresneeded

    def safeTeam(self, team):
        try:
            return int(team)
        except Exception:
            return team

    def getRequiredTeams(self):
        teamsneeded={}
        for row in self.rows:
            if not teamsneeded.has_key(row.team):
                teamsneeded[row.team]='required'
        return teamsneeded
    
    def getRules(self, measuresneeded):
        measurerules={}
        for key in measuresneeded.iterkeys():
            result=None
            try:
                result=DB.Measure.objects.get(shortname=key)
            except DB.Measure.DoesNotExist:
                result=None
            if not result:
                message='Unknown measure: %s'%key
                self.addError('base',message)
            else:
                validation=result.validation
                if validation is None:
                    validation=''
                measurerules[key]=validationrules.buildRule(validation)
        return measurerules
    
    def buildTeams(self, teamsneeded,project):
        for key in teamsneeded.iterkeys():
            resultteam=None
            try:
                resultteam=self.getTeamFromNickName(self.safeTeam(key),project)
                if not resultteam:
                    message='Unknown nickname %s'%self.safeTeam(key)
                    self.addError('base', message)
                else:
                    teamsneeded[key]=resultteam.id
            except ValueError , e:
                message='Team nickname not found: %s. %s'%(self.safeTeam(key),e)
                self.addError('base',message)
                
    def getTeamPeriods(self, teamsneeded):
        teamdata={}
        #build each team's data for each period
        for row in self.rows:
            key=(teamsneeded[row.team],row.period,row.series)
            if not teamdata.has_key(key):
                teamdata[key]={}
            if teamdata[key].has_key(row.measure):
                format='Row %i is a duplicate of row %i: %s, %s, %s'
                rownum2=teamdata[key][row.measure].rownum
                message=format%(row.rownum+1,rownum2+1, 
                    key[0],key[1], row.measure)
                self.addError('base',message)
            teamdata[key][row.measure]=row
        return teamdata
    
    def getTeamFromNickName(self, nick,project):
        
        teams=project.team_set.all()

        identifiers=DB.TeamIdentifier.objects.filter(value=nick)
        if len(identifiers)==0:
            raise ValueError('No such nickname')
            
        try:
            identifier=identifiers.get(team__in=teams)
            return identifier.team
        except AssertionError:
            raise ValueError('two teams with same nickname')
        except DB.TeamIdentifier.DoesNotExist:
            raise ValueError('No team in this project with nickname')
        
    
    def processTeamValidation(self, teamdata,measurerules):
        for databatch in teamdata.itervalues():
            for row in databatch.itervalues():
                validator=measurerules[row.measure]
                valid=validator.validate(row.value,databatch)
                if not valid:
                    format="""Measure validation failed for 
                        row %i,
                        Reason: %s."""
                    message=format%(row.rownum,validator.message)
                    self.addError('base',message)
        
    
    def build(self, filedata,reportType='Products.qi.datacapture.file.\
translate.default.PracticeTranslator'):
        logger.logText('\n\n--begining FILE build operation--')
        logger.logText('loading import type %s...'%reportType)
        self.translator=self.doImport(reportType)
        logger.logText('got importer.  creating file...')
        self.filename, self.folder=makeFile(filedata,
                self.translator.extensionType())

        path="%s/%s"%(self.folder, self.filename)
        logger.logText('file created %s... building rows'%path)
        self.buildrows(path)
        logger.logText('rows built.')
        logger.logText('--build complete--\n\n')
        
    def validate(self, dbproj, dbteam):
        logger.logText('\n\n--validation begins--')
        self.errors={}
        logger.logText('validating all rows...')
        self.validateRows()
        if self.hasErrors():
            return self.errors
        logger.logText('gathering measures...')
        measures=self.getRequiredMeasures()
        logger.logText('gathering team requirements...')
        teams=self.getRequiredTeams()
        logger.logText('building validation rules...')
        rules=self.getRules(measures)
        if self.hasErrors():
            return self.errors
        logger.logText('building teams from nicknames...')
        self.buildTeams(teams,dbproj)
        if self.hasErrors():
            return self.errors
        logger.logText('breaking data by report period and team')
        data=self.getTeamPeriods(teams)
        logger.logText('running validation rules')
        self.processTeamValidation(data,rules)
        if self.hasErrors():
            return self.errors
        logger.logText('--completed validation--\n\n')
        return self.errors
    
    def save(self, dbproj, dbteam, realname):
        logger.logText('begining save function')
        logger.logText('saving the file')
        dbfile=DB.File()
        dbfile.displayname=realname
        dbfile.name=self.filename
        dbfile.project=dbproj
        dbfile.team=dbteam
        dbfile.description='Imported data file'
        dbfile.submitted=datetime.datetime.now()
        dbfile.updated=datetime.datetime.now()
        dbfile.folder=self.folder
        dbfile.processed=datetime.datetime.now()
        dbfile.reportdate=fromExcelDate(self.rows[0].date)
        dbfile.save()
        logger.logText('file save complete')
        changes=[]
        measurementValues=[]
        self.createdSeries=[]
        logger.logText('saving rows')
        logger.resetTime()
        for row in self.rows:
            logger.logText('==saving row %s=='%row.rownum)
            self.saverow(row, dbfile, dbproj,dbteam)
        logger.logText('finished saving rows')
        logger.logText('begin logging new series')
        for series in self.createdSeries:
            logger.logText('created series: %s, for team: %s'%\
                (series,str(dbteam)))
        logger.logText('series logged, finishing save')
        
    def saverow(self, row, dbfile, dbproj, team):
        dbteam=self.getTeamFromNickName(self.safeTeam(row.team),dbproj)
        period=fromExcelDate(row.period)
        dbmeasure=DB.Measure.objects.get(shortname=row.measure)
        series=None
        if row.series is not None:
            series,created=DB.Series.objects.get_or_create(name=row.series,
                 team=dbteam)
            if created:
                self.createdSeries.append(row.series)
        try:
            if series is None:
                value=DB.MeasurementValue.objects.get(team=dbteam, \
                    itemdate=period, measure=dbmeasure, series__isnull=True)
            else:
                value=DB.MeasurementValue.objects.get(team=dbteam, \
                    itemdate=period, measure=dbmeasure, series=series)
        except DB.MeasurementValue.DoesNotExist:
            value=None
        

            
        
        if value is not None:
            v1=value.value
            v2=row.value
            a1=value.annotation
            a2=row.annotation
            
            if not self.equiv(v1,v2) or not self.equiv(a1,a2):
                logger.logText('...saving a row change')
                #the case of having to create a change and update the 
                #existing value
                change=DB.MeasurementChange()
                change.value=value
                change.oldvalue=value.value
                change.newvalue=row.value
                change.reportdate=fromExcelDate(row.date)
                change.tfile=dbfile
                change.oldannotation=value.annotation
                change.newannotation=row.annotation
                change.changedon=datetime.datetime.now()
                change.series=series
                change.save()
        else:
            value=DB.MeasurementValue()
        value.measure=DB.Measure.objects.get(shortname=row.measure)
        value.team=self.getTeamFromNickName(self.safeTeam(row.team),dbproj)
        #no team or status for team, unless we get more out of team id
        value.reportdate=fromExcelDate(row.date)
        value.itemdate=fromExcelDate(row.period)
        value.value=row.value
        value.annotation=row.annotation
        value.tfile=dbfile
        value.series=series
        value.save()
        logger.logWithElapsed('Saved row')
        
    def equiv(self,v1,v2):
        try:
            return float(str(v1))==float(str(v2))
        except ValueError:
            return str(v1)==str(v2)
        except TypeError:
            return str(v1)==str(v2)

    def addError(self, key, value):
        if self.errors.has_key(key):
            self.errors[key].append(value)
        else:
            self.errors[key]=[value,]
            
    def hasErrors(self):
        return len(self.errors)>0
            
    def getError(self, key):
        if self.errors.has_key(key):
            return self.errors[key]
        else:
            return None
    
