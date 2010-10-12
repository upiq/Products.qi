from Products.qi.datacapture.file.translate.abstract import FileTranslator
from Products.qi.datacapture.file.uploads.Row import Row
from Products.qi.datacapture.file.uploads.uploadutils import makeExcel
from Products.qi.util.logger import importlog as logger

class PracticeTranslator(FileTranslator):
    
    def __init__(self):
        self.errors={}
    def extensionType(self):
        return '.xls'
    
    def loadData(self, fileobject):
        try:
            self.rows=[]
            excel=makeExcel(fileobject)
            #sheet 1, pick data, not sheet title
            cells=excel[0][1]
            for (k, v) in cells.iteritems():
                y=k[0]
                x=k[1]
                if y!=0:
                    #expand list size as ncessary
                    if len(self.rows)<y:
                        difference=y-len(self.rows)
                        emptyList=list(None for i in range(difference))
                        self.rows[len(self.rows):]=emptyList
                    #create a row object if none exist
                    if self.rows[y-1] is None:
                        self.rows[y-1]=Row()
                        self.rows[y-1].rownum=y+1
                    row=self.rows[y-1]
                    self.loadCol(row, x, v)
        except Exception, e:
            logger.handleException(e)
            self.errors[-1]=[str(e)]
    
    def getRows(self):
        return self.rows
    
    def loadCol(self, row, colnumber, value):
        if colnumber>7:
            row.extracols=True
        if colnumber==0:
            row.date=value
        if colnumber==1:
            row.team=value
        if colnumber==2:
            row.period=value
        if colnumber==3:
            row.measure=value
        if colnumber==4:
            row.value=value
        if colnumber==5:
            row.annotation=value
        if colnumber==6:
            row.reported=value
        if colnumber==7:
            if value.upper()=='TOTAL POPULATION':
                row.series=None
            else:
                row.series=value        
            
    def getErrors(self):
        return self.errors

#reimplements the practice translator with the assumption of POF as series
class POFTranslator(PracticeTranslator):
    def loadCol(self, row, colnumber, value):
        if colnumber>7:
            row.extracols=True
        if colnumber==0:
            row.date=value
        if colnumber==1:
            row.team=value
        if colnumber==2:
            row.period=value
        if colnumber==3:
            row.measure=value
        if colnumber==4:
            row.value=value
        if colnumber==5:
            row.annotation=value
        if colnumber==6:
            row.reported=value
        if colnumber==7:
            if value.upper()=='TOTAL POPULATION':
                row.series=None
            else:
                row.series=value
        if not hasattr(row, 'series') or row.series is None:
            row.series="POF"


#reimplements the behavior of the PracticeTranslator for csv format
class CSVPracticeTranslator(PracticeTranslator):
    #needed only for the purposes of making stored files easier to get at.
    def extensionType(self):
        return '.csv'
    def loadData(self, fileobject):
        try:
            filedata=open(fileobject,'r')
            rawrows=filedata.readlines()
            self.rows=[]
            rownum=0

            for rawrow in rawrows:
                rownum=rownum+1
                if rownum>1:
                    added=Row()
                    added.datetype="dashed"
                    added.rownum=rownum
                    x=0
                    for value in rawrow.split(','):
                        value=value.strip()
                        self.loadCol(added, x, value)
                        x=x+1
                    self.rows.append(added)
                
                
        except Exception, e:
            logger.handleException(e)
            self.errors[-1]=[str(e)]