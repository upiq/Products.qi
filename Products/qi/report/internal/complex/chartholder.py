from zope.interface import implements

from interfaces import IChartHolder
from zope.component.factory import Factory
from Products.qi import MessageFactory as _
from plone.app.content.container import Container
from OFS.OrderSupport import OrderSupport
from datetime import datetime, timedelta

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from qi.sqladmin import models as DB

from Products.qi.report.internal.complex.rows.row import rowfactory

from Products.qi.report.internal.complex.rows.interfaces import IChartRow


class AggregateStandIn:
    #this is designed to stand in for a team for all the ways we use one in this charting system
    def __init__(self, aggregateType, dbproject=None, dbteam=None):
        self.proj=dbproject
        self.team=dbteam
        self.agg=aggregateType
        aggnames={'min': 'Minimum',
                    'max':'Maximum',
                    'avg':'Average'}
        if self.team:
            self.id='%s-%s'%(self.team.id, self.agg)
            self.name='%s %s'%(self.team.name, aggnames[self.agg])
        else:
            self.id='%s'%( self.agg)
            self.name='%s'%( aggnames[self.agg])
    def __hash__(self):
        return hash(self.proj)+ hash(self.team)+hash(self.agg)
    def __cmp__(self, other):
        if type(other)==CurrentTeamStandIn:
            #always let [current team] go in front
            return cmp(2,1)
        return cmp(self.id, other.id)
    def aggregate(self, widgit, measure, date):
        subteams=self.subteams()
        values=[widgit.valuefor(measure, team, date) for team in subteams]
        minimum=None
        maximum=None
        total=0.0
        count=0#omit nones in count
        for value in values:
            if value is None:
                continue
            if minimum is None:
                minimum=value
            if maximum is None:
                maximum=value
            if minimum>value:
                minimum=value
            if maximum<value:
                maximum=value
            total+=value
            count+=1
        if self.agg=='min':
            return minimum
        elif self.agg=='max':
            return maximum
        elif self.agg=='avg':
            if count!=0:
                return total/count
            else:
                return None
        raise NotImplementedError("weird aggregate detected")
                
    
    def subteams(self):
        if hasattr(self,'tempteams'):
            return self.tempteams
        if self.team:
            if  hasattr(self.team,'dbteam'):
                dbteam=self.team.dbteam
            else:
                dbteam=self.team
            result= dbteam.team_set.all()
        else:
            result=self.proj.team_set.all()
        self.tempteams=result
        return result
    def countTeams(self):
        return self.subteams().count()

class CurrentTeamStandIn:

    def __init__(self, dbteam):
        self.id='currentteam'
        self.name='[Current Team]%s'%dbteam.name
        self.dbteam=dbteam
    def __cmp__(self, other):
        if self.id==other.id:
            return cmp(0,0)
        return cmp(1,2)

class ParentStandIn:
    def __init__(self, dbteam):
        self.id='parentteam'
        self.name='[Parent Team]%s'%dbteam.name
        self.dbteam=dbteam
    
    
        
        
    
    
    
def buildTeamStandIns(team):
    return [
    AggregateStandIn('min', dbteam=team),
    AggregateStandIn('max', dbteam=team),
    AggregateStandIn('avg', dbteam=team),
    ]
def buildProjectStandIns(proj):
    return [
    AggregateStandIn('min', dbproject=proj),
    AggregateStandIn('max', dbproject=proj),
    AggregateStandIn('avg', dbproject=proj),
    ]

def sortrow(a,b):
    return cmp(a.rownum(),b.rownum())


class ChartHolder(BrowserDefaultMixin, OrderSupport, Container):
    implements(IChartHolder,)
    title=""
    description=""
    portal_type="qi.ChartHolder"
    maxwidth=0
    rowid=1
    perseverate=False
    
    def __init__(self):
        self.rowid=1
        self.cachetime=None

    def rows(self):
        assignedrows=[x for x in self.getChildNodes() if IChartRow.isImplementedBy(x)]
        result=sorted(assignedrows,sortrow)
        return result
    
    def addRow(self, index):
        added=rowfactory()
        added.location=self.rowid
    
        if index!=-1:
            for row in self.rows():
                if row.rowindex>=index:
                    row.rowindex+=1
        elif len(self.rows())>0:
            index=max([x.rowindex for x in self.rows()])+1
        else:
            index=1
        self.rowid+=1
        name='row-%i'%self.rowid
        added.id=name
        added.rowindex=index
        added.title=name
        self._setObject(name,added)
        self.orderObjects('rowindex',False)
    def charturl(self):
        return self.absolute_url()
    
    def getGlobalMeasures(self):
        projectmeasures=self.getDBProject().projectmeasure_set.all()
        regularmeasures=[x.measure for x in projectmeasures]
        aggregatemeasures=[x for x in self.getDBProject().derivedmeasurevalue_set.all()]
        return regularmeasures+aggregatemeasures
    
    def getGlobalTeams(self):
        project, team=self.getProjectTeam()
        if team:
            result=[CurrentTeamStandIn(team)]
            result.extend(sorted(team.team_set.all()))
            teamobj=result[0]
        else:
            teamobj=None
            result=list(sorted(project.team_set.all()))
        #also include all aggregate teams
        result.extend(sorted(self.getAggregateTeams(teamobj)))
        return result
        
    def getProjectTeam(self):
        project=self.getDBProject()
        try:
            team=self.getDBTeam()
        except AttributeError:
            team=None
        return project, team
        
    def getAggregateTeams(self,teamobj=None):
        project, team=self.getProjectTeam()
        if team and team.team_set.count()>0:
            return buildTeamStandIns(teamobj)
        elif team and team.parent:
            return buildTeamStandIns(ParentStandIn(team.parent))
        elif not team:
            result=buildProjectStandIns(project)
            for team in project.team_set.all():
                if team.team_set.count()>0:
                    result.extend(buildTeamStandIns(team))
            return result
            
        
    def getGlobalDates(self,teams=None, measures=None):
        if teams is None:
            teams=self.getGlobalTeams()
        if measures is None:
            measures=self.getGlobalMeasures()
        checkedteams=set()
        """for x in teams:
            if isinstance(x, DB.Team):
                checkedteams.add(x)
                checkedteams=checkedteams | set(x.dbteam.team_set.all())
            elif hasattr(x, 'dbteam'):
                checkedteams.add(x.dbteam)
                checkedteams=checkedteams | set(x.dbteam.team_set.all())
            else:
                checkedteams.extend(self.getDBProject().team_set.all())"""
        checkedteams=self.getDBProject().team_set.all()
        return DB.MeasurementValue.datesfor(checkedteams, measures)
        



chartFactory = Factory(ChartHolder, title=_(u"Create a new online report"))
