from interfaces import IWidgit, IDataTable
from zope.interface import implements
from zope.component.factory import Factory
from Persistence import Persistent
from plone.app.content.container import Container

from Products.Five.browser import BrowserView

from Products.qi.report.internal.complex.interfaces import IChartHolder
from Products.qi.report.internal.complex.chartholder import AggregateStandIn, CurrentTeamStandIn
from qi.sqladmin import models as DB

from datetime import datetime

from Products.qi.report.internal.complex.filter.filter import AllFiltered

class ResultVal:
    def __init__(self, value, note):
        self.value=value
        self.note=note

class Widgit(Container, AllFiltered):
    widgitname='generic widgit'
    implements(IWidgit)
    printonly=False
    def typename(self):
        return "unknown report object"
        
    def full_team_set(self):
        if hasattr(self, 'getDBTeam'):
            ownteam=self.getDBTeam()
            children=ownteam.team_set.all()
            result=[x for x in children]
            x.append(self)
        else:
            return self.getDBProject().team_set.all()
    
    def teams(self):
        return self.getTeams()
        """
        allteams=self.full_team_set()
        filterer=self.hasTeamFilter()
        teams=self.filterer.filter(allteams)
        return self.getDBProject().team_set.all()"""
    def measures(self):
        return self.getMeasures()
        """
        projectMeasures=DB.ProjectMeasure.objects.filter(project=self.getDBProject())
        return [x.measure for x in projectMeasures]"""
    def dates(self):
        return self.getDates()
    

            
    def populatevalues(self):
        alldatadict={}
        for measure in self.measures():
            measuredict={}
            alldatadict[measure]=measuredict
            for team in self.teams():
                teamdict=self.buildline(measure, team)
                measuredict[team]=teamdict
                #TODO get the values packed in, hopefully with a minimum of computation
            
        self.REQUEST['measures']=alldatadict
    def buildline(self,measure, team):
        if isinstance(team,AggregateStandIn):
            if not team.team:
                records=measure.getValues(aggregate=team.agg, project_id=team.proj.id)
            else:
                records=measure.getValues(team_id=team.team.id,aggregate=team.agg)
        else:
            records=measure.getValues(team_id=team.id)
        result={}
        for period,note,value in records:
            
            result[period]=ResultVal(value, note)
        return result
            
    def valuefor(self, measure,team,date):
        request=self.REQUEST
        #print request.get('measures','fake result')
        
        if not request.get('measures',None):
            self.populatevalues()
        return request.get('measures',{}).get(measure,{}).get(team,{}).get(date,ResultVal(None,None)).value
        #return request.get('measures').get(measure,{}).get(team,{}).get(date,None)
        if isinstance(measure,DB.Measure):
            #simple case return straight from db
            if isinstance(team, AggregateStandIn):
                #defer the details of aggregation
                return team.aggregate(self, measure, date)
            elif isinstance(team, CurrentTeamStandIn):
                return self.valuefor(measure,team.dbteam,date)
            else:
                #seperate this method because it's complicated
                result=self.simpleValue(measure, team,date)
                try:
                    #since we're charting we want numbers and decimals places can be handy
                    return float(result)
                except (TypeError, ValueError):
                    return None
        elif isinstance(measure, DB.DerivedMeasureValue):
            if isinstance(team, AggregateStandIn):
                return team.aggregate(self,measure,date)
                return measure.getValue(team.id, date, self.perseverate)
            elif isinstance(team, CurrentTeamStandIn):
                return self.valuefor(measure,team.dbteam,date)
            else:
                return measure.newGetValue(team, date,  self.perseverate)
    def notefor(self, measure, team, date):
        request=self.REQUEST
        #print request.get('measures','fake result')
        
        if not request.get('measures',None):
            self.populatevalues()
        return request.get('measures',{}).get(measure,{}).get(team,{}).get(date,ResultVal(None,None)).note
        if isinstance(measure,DB.Measure):
            #simple case return straight from db
            if isinstance(team, AggregateStandIn):
                #defer the details of aggregation
                return "%s of %s teams"%(team.name,team.countTeams())
            elif isinstance(team, CurrentTeamStandIn):
                return self.notefor(measure,team.dbteam,date)
            else:
                #seperate this method because it's complicated
                try:
                    return DB.MeasurementValue.objects.get(measure=measure, team=team, itemdate=date).annotation
                except DB.MeasurementValue.DoesNotExist:
                    return ""
                return result
        elif isinstance(measure, DB.DerivedMeasureValue):
            if isinstance(team, AggregateStandIn):
                return "%s calculated value of %s teams"%(team.name,team.countTeams())
            elif isinstance(team, CurrentTeamStandIn):
                return self.notefor(measure,team.dbteam,date)
            else:
                return "Calculated value"
    
        
    def simpleValue(self, measure, team, date):
        try:
            result= DB.MeasurementValue.objects.get(series__isnull=True,
                itemdate=date, team=team,measure=measure)
            return float(result.value)
        except DB.MeasurementValue.DoesNotExist:
            pass
        except (TypeError,ValueError):
            print 'RUH ROH\n\n\n\n'
            #non-floats are a problem
            return None
        if self.perseverate:
            #if we're set to perseverate, attempt to
            try:           
                return float(DB.MeasurementValue.objects.filter(series__isnull=True,
                    itemdate__lte=date, team=team,measure=measure).latest('reportdate').value)
            except DB.MeasurementValue.DoesNotExist:
                print 'fail',DB.MeasurementValue.objects.filter(series__isnull=True,
                    itemdate__lte=date, team=team,measure=measure)
                pass
            except (TypeError,ValueError), e:
                print e
                return None
        #if we don't perseverate, or we STILL can't find a suitable value backwards in time
        #then skip that spot in the graph
        return None
    
    def updateOtherAttribute(self, attribute, value):
        raise NotImplementedError("%s was not a valid attribute to assign"%attribute)
    
    def printblurb(self):
        #unless only charts have distinct display and print blurbs
        return self.displayblurb()


class KeyWrapper:
    keyname=None
    name=None
    data=None
    def __init__(self, keyname, name, data):
        self.keyname=keyname
        self.name=name
        self.data=data
    def __str__(self):
        return 'key: %s %s %s'%(self.keyname,self.name, self.data)
        
def appendlist(current,added):
    if len(current)==0:
        return [(x,) for x in added]
    newlist=[]
    for x in current:
        for y in added:
            newlist.append(x+(y,))
    return newlist
    

class DataTable(Widgit):
    widgitname='data table'
    implements(IDataTable)
    order=['Team','Date','Measure']
    
    def typename(self):
        return "Data Table"
    def swapdown(self, swapped):
        #create a new order to preserve the default sorting
        #which is essential for healthy display of this object
        neworder=self.order[:]
        index=neworder.index(swapped)
        neworder.remove(swapped)
        neworder.insert(index+1, swapped)
        self.order=neworder
        
    def keyheight(self):
        return range(len(self.order[2:]))
        
    def wrapKeys(self, keyname, keys):
        if keyname in ('Measure','Team'):
            return [KeyWrapper(keyname, x.name,x) for x in keys]
        elif keyname=='Date':
            return [KeyWrapper(keyname, 
                                '%i/%i/%i'%(x.month,x.day,x.year)
                                ,x)
                    for x in keys]
    
    def buildKeysFrom(self,keynames):
        result=[]
        combined=[]
        for keyname in keynames:
            if keyname=='Team':
                keys=self.teams()
            if keyname=='Date':
                keys=self.dates()
            if keyname=='Measure':
                keys=self.measures()
            combined.append(self.wrapKeys(keyname,keys))
        resultset=[]
        for keyset in combined:
            resultset=appendlist(resultset, keyset)
        return resultset
    def rowkeys(self):
        return self.buildKeysFrom(self.order[:2])
    def columnkeys(self):
        return self.buildKeysFrom(self.order[2:])
        
        
    def valuebykeys(self, rowkey, columnkey):
        teamname=None
        date=None
        measure=None
        for datasource in rowkey+columnkey:
            if datasource.keyname=='Measure':
                measure=datasource
            if datasource.keyname=='Team':
                team=datasource
            if datasource.keyname=='Date':
                date=datasource
        result= self.valuefor(measure.data,team.data,date.data)
        if result is None:
            return 'No value'
        return result
        
class NoteTable(DataTable):
    allowsderivedmeasures=False
    allowaggregateteams=False
    def valuefor(self, measure,team,date):
        return self.notefor(measure,team,date)


class Swap(BrowserView):
    def __call__(self):
        form=self.request.form
        swapped=form['swapped']
        self.context.swapdown(swapped)
        redirectTarget="%s/design"%self.context.charturl()
        self.request.response.redirect(redirectTarget)
    
    
annotationfactory=Factory(NoteTable, title="annotation table")
tablefactory=Factory(DataTable,title="add a table")