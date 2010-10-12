from qi.sqladmin import models as DB
from Products.qi.datacapture.validation.validationrules import buildRule, InvalidExpression
from Row import TranslatedRow
class UploadBuilder:
    def __init__(self, upload):
        self.upload=upload
        self.requiredMeasures={}
        self.requiredTeams={}
        self.validators={}
    
    #takes untranslated rows
    def getRequirements(self):
        for row in self.upload.rows:
            if isinstance(row.team, list):
                teamname=tuple([str(x).strip() for x in row.team])
            else:
                teamname=str(row.team).strip()
            measurename=str(row.measure).strip()
            if measurename not in self.requiredMeasures:
                self.requiredMeasures[measurename]=row
            if teamname not in self.requiredTeams:
                
                self.requiredTeams[teamname]=row
    
    def buildRequirements(self):
        self.findRequiredMeasures()
        self.findRequiredTeams()

    
    def findRequiredTeams(self):
        for team in self.requiredTeams.iterkeys():
            dbteam=self.getTeam(team)
            rownum=self.requiredTeams[team].rownum
            if dbteam is None:
                try:
                    teamname=str(int(float(team)))
                except:
                    teamname=str(team)
                self.upload.addError(rownum,'Team nickname "%s" could not be found.  Required by row %i'%(teamname,rownum))
            else:
                self.requiredTeams[team]=dbteam
    def findRequiredSeries(self):
        for series in self.requireSeries.iterkeys():
            dbseries=self.getSeries(series)
            rownum=self.requiredSeries[series]
            if dbseries is None:
                self.upload.addError(rownum,'Series "%s" could not be created.  Required by row %i'%(series,rownum))
            else:
                self.requiredSeries[series]=None
                
    def findRequiredMeasures(self):
        for measure in self.requiredMeasures.iterkeys():
            dbmeasure=self.getMeasure(measure)
            rownum=self.requiredMeasures[measure].rownum
            if dbmeasure is None:
                self.upload.addError(rownum,'Measure "%s" could not be found.  Required by row %i'%(measure,rownum))
            else:
                self.requiredMeasures[measure]=dbmeasure
                self.findValidator( dbmeasure,measure)

    def findValidator(self, dbmeasure, measure):
        validation=self.buildValidation(dbmeasure)
        if validation is None:
            error='Validation rule could not be compiled for measure "%s"'
            self.upload.addError(-1,error%(measure))
        else:
            self.validators[measure]=validation
        
    
    def handleRequirements(self):
        self.getRequirements()
        self.buildRequirements()
    
    def getTeamPeriods(self, teamsneeded):
        teamdata={}
        #build each team's data for each period
        for row in self.upload.rows:
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
        
    def getTeam(self, nick):
        #shoe-horn in a lookup for NCIPIP export/import
        print type(nick), nick
        if isinstance(nick,tuple):
            for x in nick:
                result= self.getTeam(x)
                print 'team lookup: ', x, result
                if result:
                    return result
            return None
        try:
            newnick=str(int(float(nick)))
        except:
            newnick=nick
        teams=self.upload.dbproj.team_set.all()

        identifiers=DB.TeamIdentifier.objects.filter(value=newnick)
        try:
            identifier=identifiers.get(team__in=teams)
            return identifier.team
        except AssertionError:
            return None
        except DB.TeamIdentifier.DoesNotExist:
            return None
        return None
    
    def getMeasure(self,measure):
        try:
            return DB.Measure.objects.get(shortname=measure)
        except DB.Measure.DoesNotExist:
            try:
                return DB.Measure.objects.get(name=measure)
            except DB.Measure.DoesNotExist:
                pass
        return None
    def buildValidation(self, dbmeasure):
        try:
            if dbmeasure.validation is None:
                rule=buildRule("")
            else:
                rule=buildRule(dbmeasure.validation)
            return rule
        except InvalidExpression: 
            return None
            
    #does a python import to get the processing tool    
    def getRequiredMeasures(self):
        measuresneeded={}
        for row in self.upload.rows:
            measuresneeded[row.measure]=row.rownum
        upload.requiredMeasures=measuresneeded
        
    def getRequiredTeams(self):
        teamsneeded={}
        for row in self.upload.rows:
            teamsneeded[row.team]=row.rownum
        upload.requiredTeams=teamsneeded
        

    def translateRows(self):
        self.upload.translated=[TranslatedRow(row,self) for row in self.upload.rows]
    




