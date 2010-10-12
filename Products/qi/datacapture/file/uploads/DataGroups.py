from qi.sqladmin import models as DB
from datetime import datetime
from Products.qi.datacapture.validation.validationrules import buildRule
from Products.qi.util.logger import importlog as logger

class DuplicateEntry(Exception):
    def __init__(self, existingrow=-1, newrow=-1):
        self.existingrow=existingrow
        self.newrow=newrow
class DataIntegrityProblem(Exception):
    pass
        

class AllData:
    def __init__(self, fileobj):
        self.dbfile=fileobj
        self.teams={}
        self.duplicates=[]
    def addrows(self, translatedrows):
        for row in translatedrows:
            try:
                self.addrow(row)
            except DuplicateEntry, e:
                self.duplicates.append(e)
    def addrow(self, row):
        if row.team in self.teams:
            teamobj=self.teams[row.team]
        else:
            teamobj=TeamData(row.team)
            self.teams[row.team]=teamobj
        teamobj.insert(row)
    #contract:
    #return a list of tuples
    #(measurementvalue, measurementchange)
    #measurement values will be created if necessary and will never be none
    #changes will be created if required(value does not exist, and is not equivalent)
    def getAllEntries(self):
        currentEntries=DB.MeasurementValue.objects.all()
        result=[]
        for team in self.teams.itervalues():
            result.extend(team.getAllEntries(currentEntries))
        for value, changeset in result:
            value.tfile=self.dbfile
            for change in changeset:
                if change.tfile is None:
                    change.tfile=self.dbfile
        return result
    def runValidation(self):
        result=[]
        for duplicate in self.duplicates:
            errorMessage="Row %i duplicates row %i"%(duplicate.existingrow,duplicate.newrow)
            result.append((duplicate.newrow,errorMessage,10))
        if len(result)!=0:
            return result
        for team in self.teams.itervalues():
            result.extend(team.runValidation())
        return result
        
        
class TeamData:
    def __init__(self, dbteam):
        self.dbteam=dbteam
        self.serieses={}
    def insert(self, row):
        if row.series in self.serieses:
            series=self.serieses[row.series]
        else:
            series=Series(row.series, self.dbteam)
            self.serieses[row.series]=series
        series.insert(row)
    
    def getAllEntries(self, entrySet):
        subset=entrySet.filter(team=self.dbteam)
        result=[]
        for series in self.serieses.itervalues():
            result.extend(series.getAllEntries(subset))
        for value, changeset in result:
            value.team=self.dbteam
        return result
    def runValidation(self):
        result=[]
        for series in self.serieses.itervalues():
            result.extend(series.runValidation())
        return result

class Series:
    def __init__(self, seriesname, dbteam):

        if seriesname is None or seriesname.lower()=="total population":
            self.series=None
        else:
            self.series, meh=DB.Series.objects.get_or_create(name=str(seriesname).strip(), team=dbteam)
            if meh:
                logger.logText("created a series %s"%seriesname)
        self.periods={}
    def insert(self,row):
        if row.period in self.periods:
            periodobj=self.periods[row.period]
        else:
            periodobj=Period(row.period)
            self.periods[row.period]=periodobj
        periodobj.insert(row)
    def getAllEntries(self, entrySet):
        if self.series is None:
            subset=entrySet.filter(series__isnull=True)
        else:
            subset=entrySet.filter(series=self.series)
        result=[]
        for period in self.periods.itervalues():
            result.extend(period.getAllEntries(subset))
        for value, changeset in result:
            value.series=self.series
        return result
    def runValidation(self):
        result=[]
        for period in self.periods.itervalues():
            result.extend(period.runValidation())
        return result
class Period:
    def __init__(self,period):
        self.period=period
        self.measures={}
    def insert(self, row):
        if row.measure in self.measures:
            measureobj=self.measures[row.measure]
        else:
            measureobj=MeasurementEntry(row.measure)
            self.measures[row.measure]=measureobj
        measureobj.insert(row)
    def getAllEntries(self, entrySet):
        result=[]
        subset=entrySet.filter(itemdate=self.period)
        for measure in self.measures.itervalues():
            result.append(measure.getEntry(subset))
        for value, changeset in result:
            value.itemdate=self.period
        return result
    def runValidation(self):
        result=[]
        passedMeasures={}
        for m in self.measures.iterkeys():
            name=m.shortname
            passedMeasures[name]=self.measures[m]
        for measure in self.measures.itervalues():
            value=measure.runValidation(passedMeasures)
            if value is not None:
                result.append(value)
        return result
class MeasurementEntry:
    def __init__(self, dbmeasure):
        self.measure=dbmeasure
        self.latestdate=None
        self.otherdates={}
    def insert(self, row):
        added=None
        if self.latestdate is None:
            self.latestdate=ReportingDate(row.date)
            added=self.latestdate
        elif self.latestdate.date< row.date:
            self.otherdates[self.latestdate.date]=self.latestdate
            self.latestdate=ReportingDate(row.date)
            added=self.latestdate
        elif self.latestdate.date==row.date:
            raise DuplicateEntry(self.latestdate.rownum,row.rownum)
        elif row.date in self.otherdates:
            raise DuplicateEntry(self.otherdates[row.date].rownum,row.rownum)
        else:
            self.otherdates[row.date]=ReportingDate(row.date)
            added=self.otherdates[row.date]
        added.insert(row)
    def getEntry(self, entrySet):
        
        subset=entrySet.filter(measure=self.measure)
        value=None
        #also a value that we CREATE!
        changes=[]
        #these are specifically CHANGES CREATED BY US
        if len(subset)==0:
            #create the first
            value=self.latestdate.createValue()
            #create all changes
            for key in self.otherdates:
                dateobj=self.otherdates[key]
                added=dateobj.createChange(None)
                if added is not None:
                    changes.append(added)
        elif len(subset)==1:
            obj=subset[0]
            if obj.reportdate>self.latestdate.date:
                self.otherdates[self.latestdate.date]=self.latestdate
                value=obj
            else:
                change=self.createChangeFrom(obj)
                changes.append(change)
                value=self.latestdate.createValue(obj)                
            for key in self.otherdates:
                dateobj=self.otherdates[key]
                added=dateobj.createChange(obj)
                if added is not None:
                    changes.append(added)   
        else:
            raise DataIntegrityProblem(str(subset))
        if value is None:
            raise DataIntegrityProblem()
        for change in changes:
            change.value=value
            change.newvalue=value.value
            change.newannotation=value.annotation
            change.changedon=datetime.today()
        #even if this is already set...
        value.measure=self.measure
        return value, changes
    def runValidation(self, otherMeasures):
        
        validation=self.measure.validation
        if validation is None:
            validation=""
        rule=buildRule(validation)
        validation=rule.validate(self.latestdate.value,otherMeasures)
        if validation==0:
            return None
        else:
            return (self.latestdate.rownum,"%s: %s"%(self.measure.name,rule.message),validation)
    def createChangeFrom(self, oldDBvalue):
        result=DB.MeasurementChange()
        result.oldvalue=oldDBvalue.value
        result.oldannotation=oldDBvalue.annotation
        result.reportdate=oldDBvalue.reportdate
        result.tfile=oldDBvalue.tfile
        return result
        

class ReportingDate:
    def __init__(self, date):
        self.date=date
        self.value=None
        self.annotation=None
        self.rownum=None
    
    def createValue(self,existing=None):
        if existing is None:
            value=DB.MeasurementValue()
        else:
            value=existing
        value.reportdate=self.date
        value.value=self.value
        value.annotation=self.annotation
        return value
    
    def createChange(self, value):
        """if value is not None:
            try:
                value.measurementchange_set.get(reportdate=self.date)
                return None
            except DB.MeasurementChange.DoesNotExist:
                pass
            """
        result=DB.MeasurementChange()
        result.reportdate=self.date
        result.oldannotation=self.annotation
        result.oldvalue=self.value
        return result
        
        
    def insert(self, row):
        self.value=row.value
        self.annotation=row.annotation
        self.rownum=row.rownum
        
    def getValueChange(self, entrySet, latest):
        result=[]
        return result

