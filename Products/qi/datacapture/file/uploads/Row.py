import uploadutils
from datetime import date
from Products.qi.util.logger import importlog as logger

class TranslatedRow:
    def __init__(self, row, builder):
        if isinstance(row.team, list):
            teamname=tuple([x.strip() for x in row.team])
        else:
            teamname=str(row.team).strip()
        self.date=row.extractDate(row.date)
        self.measure=builder.requiredMeasures[str(row.measure).strip()]
        self.period=row.extractDate(row.period)
        #logger.logText('this is what is available: '+str(builder.requiredTeams))
        self.team=builder.requiredTeams[teamname]
        self.value=row.value
        self.annotation=row.annotation
        if hasattr(row, 'series') and row.series is not None:
            seriesname=str(row.series).strip()
            self.series=seriesname
        else:
            self.series=None
        self.rownum=row.rownum
        self.rule=builder.validators[row.measure.strip()]

class Row:
    date=None #expects date formatted string
    measure=None
    period=None #expects date formatted string
    team=None #a num num num number
    value=None #generally expects a number of some kind
    annotation=None #this is NOT validated
    series=None
    extracols=False
    rownum=-1
    datetype="excel"
    
    def __str__(self):
        return "%s, %s, %s: %s \n"%(self.period, self.measure, self.team,self.value)
    def __repr__(self):
        return self.__str__()
    
    def validate(self):
        if not self.date:
            return 'Report date'
        if not self.validDate(self.date):
            return 'Report date'
        #MEASURE not required
        if not self.period:
            return 'Period'
        if not self.validDate(self.period):
            return 'Period'
        if self.team is None:
            return 'Team'
        if self.value is None:
            self.value=""
        
        if self.extracols:
            return 'Extra Columns'
        if self.measure is None or str(self.measure).strip()=="":
            return "Measure"
        
        return None
        
    def validDate(self, datestring):
        if isinstance(datestring,date):
            return True
        if self.datetype=="excel":
            try:
                #if it can't be treated as an int it's not a valid excel date
                int(float(datestring))
            except ValueError:
                return False
            return True
        elif self.datetype=="dashed":
            parts=datestring.split("-")
            if len(parts)!=3:
                return False
            return True
        return False
    def extractDate(self,dateobj):
        if isinstance(dateobj,date):
            return dateobj
        if self.datetype=="excel":
            return uploadutils.fromExcelDate(dateobj)
        elif self.datetype=="dashed":
            return uploadutils.fromDashedDate(dateobj)
        else:
            return None

#used by square style import routines
class ComputedRow(Row):
    def validDate(self, dateobj):
        return True
    def extractDate(self,dateobj):
        return dateobj

from datetime import date
from qi.sqladmin import models as DB
def fastrow():
    row=Row()
    row.date=date.today()
    row.period=date(2008,11,1)
    row.value="testvalue"
    row.annotation="test note"
    row.measure=DB.Measure.objects.all().order_by('-id')[0]
    row.team=DB.Team.objects.all()[0]
    row.series=None
    return row