

from interfaces import IDataFilter
from qi.sqladmin import models as DB
from Products.qi.report.internal.complex.chartholder import AggregateStandIn

from zope.interface import implements

class TeamFiltered:
    _teamlist=None
    multiteam=True
    allowaggregateteams=True
    def possibleTeams(self):
        result=self.getGlobalTeams()
        if self.allowaggregateteams:
            return result
        return [x for x in result if not isinstance(x, AggregateStandIn)]
    
    def getTeams(self):
        if self._teamlist is None:
            result= self.possibleTeams()
        else:
            result=[x for x in self.possibleTeams() if str(x.id) in self._teamlist]
        if self.multiteam or len(result)==0:
            return result
        else:
            return result[:1]
        
    def setTeams(self, teams):
        self._teamlist=teams
        

class MeasureFiltered:
    _measures=None
    multimeasure=True
    allowsderivedmeasures=True
    
    def possibleMeasures(self):
        result=self.getGlobalMeasures()
        if self.allowsderivedmeasures:
            return result
        return [x for x in result if not isinstance(x, DB.DerivedMeasureValue)]
    
    def getMeasures(self):
        if self._measures is None:
            result=self.possibleMeasures()
        else:
            result=[x for x in self.possibleMeasures() if self.checkMeasure(x)]
        if self.multimeasure or len(result)==0:
            return result
        else:
            return result[:1]
    
    def checkMeasure(self, measure):
        return self.getIdForMeasure(measure) in self._measures
    
    def setMeasures(self, measures):
        self._measures=measures
    
    def getIdForMeasure(self,measure):
        isderived=isinstance(measure, DB.Percentage)
        added=""
        if isderived:
            #I realized there might be a measure and a derived measure with the same id
            added="d"
        return str(measure.id)+added
    
        

class DateFiltered:
    _startdate=None
    _enddate=None
    
    def getDates(self):
        return [x for x in self.getGlobalDates() if self.fits(x)]
    def setDates(self, start, end):
        self.dates=datelist
    def fits(self, date):
        return True
        
class AllFiltered(TeamFiltered,MeasureFiltered,DateFiltered):
    implements(IDataFilter)
    