
from interfaces import IBigChart, IControlChart
from zope.interface import implements
from Products.Five.browser import BrowserView

from zope.component.factory import Factory

from qi.sqladmin import models as DB

from Products.qi.report.internal.complex.widgits.chart import Chart



class BigChart(Chart):
    implements(IBigChart)

class TeamChart(BigChart):
    widgitname='Team Chart'
    charttype='Team'
    multiteam=False
    def chartTitle(self):
        return self.getTeams()[0].name

class MeasureChart(BigChart):
    widgitname='Measure Chart'
    charttype='Measure'
    multimeasure=False
    def chartTitle(self):
        return self.getMeasures()[0].name

class ControlChart(BigChart):
    widgitname='Control Chart'
    charttype='Control'
    multimeasure=False
    multiteam=False
    usesWarnings=True
    implements(IControlChart)
    def chartTitle(self):
        return '%s Control Chart'%self.getMeasures()[0].name
    
from math import sqrt
class ControlChartData(BrowserView):
    def __call__(self, *args, **kw):
        return self.index(self, *args, **kw)
    _mean=None
    def mean(self):
        if self._mean:
            return self._mean
        data=self.getData()
        result= sum(data)/len(data)
        self._mean=result
        return result
    _stddev=None
    def stddev(self):
        if self._stddev:
            return self._stddev
        mean=self.mean()
        data=self.getData()
        results=[(x-mean)**2 for x in data]
        result=sqrt(sum(results)/len(results))
        self._stddev=result
        return result
    _stderr=None
    def stderr(self):
        if self._stderr:
            return self._stderr
        data=self.getData()
        result=self.stddev()/sqrt(float(len(data)))
        self._stderr=result
        return result
    _data=None
    _databydate=None
    def getData(self):
        if self._data:
            return self._data
        measure=self.context.getMeasures()[0]
        team=self.context.getTeams()[0]
        databydate={}
        data=[]
        for date in self.context.getDates():
            value=self.context.valuefor(measure, team, date)
            data.append(value)
            databydate[date]=value
        self._data=data
        self._databydate=databydate
        return self._data
    def getDataByDate(self):
        if self._databydate:
            return self._databydate
        self.getData()
        return self._databydate
    _UCL=None
    def UCL(self):
        if self._UCL:
            return self._UCL
        self._UCL=3*self.stderr()+self.mean()
        return self._UCL
    _LCL=None
    def LCL(self):
        if self._LCL:
            return self._LCL
        self._LCL=-3*self.stderr()+self.mean()
        return self._LCL
    _UCW=None
    def UCW(self):
        if self._UCW:
            return self._UCW
        self._UCW=2*self.stderr()+self.mean()
        return self._UCW
    _LCW=None
    def LCW(self):
        if self._LCW:
            return self._LCW
        self._LCW=-2*self.stderr()+self.mean()
        return self._LCW
            
        
measurefactory=Factory(MeasureChart,title="measure chart")
teamfactory=Factory(TeamChart,title="team chart")
controlfactory=Factory(ControlChart,title="control chart")