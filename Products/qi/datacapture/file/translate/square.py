##Added to qiteamspace with:
## Products.qi.datacapture.file.translate.square.SquareTranslator

from Products.qi.datacapture.file.translate.abstract import FileTranslator
from Products.qi.datacapture.file.uploads.Row import ComputedRow as Row
from Products.qi.datacapture.file.uploads.uploadutils import makeExcel
from Products.qi.util.logger import importlog as logger
from datetime import date


class DataStructureProblem(Exception):
    pass

class Column:
    def __init__(self):
        self.title="Untitled"
        self.rows={}
        self.data=None
    def compileData(self, rowcount):
        self.data=[None for x in range(rowcount)]
        for rownum in self.rows:
            if rownum>len(self.data):
                logger.logText("bad data at %s, data is %s.  Requested rownum: %s"%(self.title,self.data,rownum))
                raise DataStructureProblem
            if self.rows[rownum] is None:
                raise DataStructureProblem
            self.data[rownum-1]=self.rows[rownum]
    def insert(self,rownum,value):
        self.rows[rownum]=value
    
            
            

class SquareTranslator(FileTranslator):
    def __init__(self):
        self.errors={}
    def extensionType(self):
        return '.xls'
        
    def loadData(self,fileobject):
        try:
            excel=makeExcel(fileobject)
            mainsheet=excel[0]
            title=mainsheet[0]
            cells=mainsheet[1]
            self.buildColumns(cells)
            self.buildData(cells)
            #we're done reading from the spreadsheet now
            self.extractCols()
            self.buildPeriods()
        except Exception, e:
            logger.handleException(e)
            self.errors[-1]=str(e)
        
    def buildColumns(self, cells):
        self.columns={}
        self.highest=0
        for cellLocation in cells:
            rownum=cellLocation[1]
            if rownum-1>self.highest:
                self.highest=rownum-1
            value=cells[cellLocation]
            if cellLocation[0]==0:
                newcol=Column()
                newcol.title=value
                
                self.columns[cellLocation[1]]=newcol
    def buildData(self, cells):
        for cellLocation in cells:
            value=cells[cellLocation]
            row=cellLocation[0]
            colnum=cellLocation[1]
            if row>0:
                self.columns[colnum].insert(row,value)
        for col in self.columns.values():
            col.compileData(self.highest)
    def extractCols(self):
        self.IDCol=None
        self.FacIDCol=None
        self.MonthCol=None
        self.YearCol=None
        self.NotesCol=None
        titles=[x.title for x in self.columns.values()]
        newcols=[]
        for columnnum in self.columns:
            column=self.columns[columnnum]
            if column.title.lower()=="id":
                self.IDCol=column
            elif column.title.lower()=="facid":
                self.FacIDCol=column
            elif column.title.lower()=="opqc scheduled date month":
                self.MonthCol=column
            elif column.title.lower()=="opqc scheduled date year":
                self.YearCol=column
            elif column.title.lower()=="title":
                self.NotesCol=column
            else:
                newcols.append(column)
        self.columns=newcols
    def buildPeriods(self):
        dateCol=Column()
        self.reportingDate=date.today()
        dateCol.title="Reporting Period"
        dateCol.data=[None for x in range(len(self.MonthCol.data))]
        for x in range(len(self.MonthCol.data)):
            monthstring=self.MonthCol.data[x]
            yearstring=self.YearCol.data[x]
            if monthstring and yearstring:
                added=date(int(yearstring),int(monthstring),1)
            else:
                added=None
            dateCol.data[x]=added
        self.dateCol=dateCol
    def getRows(self):
        rows=[]
        logger.logText("starting to get rows for opqc square file")
        for column in self.columns:
            measurename=column.title
            for i in range(len(column.data)):
                measurevalue=column.data[i]
                if measurevalue is None:
                    #don't add anything like that
                    continue
                added=Row()
                added.measure=measurename
                added.date=self.reportingDate
                try:
                    added.period=self.dateCol.data[i]
                except:
                    logger.logText("number %i"%i)
                    logger.logText("datecol data %s"%self.dateCol.data)
                    raise
                added.team=self.FacIDCol.data[i]
                added.series=self.IDCol.data[i]
                added.annotation=self.NotesCol.data[i]
                added.value=measurevalue
                added.rownum=i+2
                rows.append(added)
        #logger.logText(" ".join([str(row) for row in rows]))
        return rows
    def getErrors(self):
        return self.errors