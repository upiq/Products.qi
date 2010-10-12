from Products.qi.datacapture.file.translate.abstract import FileTranslator
from Products.qi.datacapture.file.uploads.uploadutils import *
from Products.qi.datacapture.file.uploads.Row import Row
from Products.qi.util.logger import importlog as logger
from datetime import date

class PracticeTranslator(FileTranslator):
    def loadData(self, filepath):
        self.errors={}
        try:
            exceldata=makeExcel(filepath)
            page1data=exceldata[0][1]
            self.practiceid=page1data[(6,2)]
            self.globalseries=page1data[(7,2)]
            if self.globalseries.strip().lower()=="total population":
                self.globalseries=None
            self.globaldate=date.today()
            self.alldata=[]
            for page in exceldata:
                pagetitle=page[0]
                data=page[1]
                if pagetitle.lower().find("dm_data")>-1:
                    self.alldata.extend(self.loaddatapage(data, 24))
                if pagetitle.lower().find("asthma_data")>-1:
                    self.alldata.extend(self.loaddatapage(data, 12))
        except Exception, e:
            self.errors[-1]=e
            logger.handleException(e)
    
    def getErrors(self):
        return self.errors
        
    def loaddatapage(self, data, rejectafter):
        builtdata=[]
        for cellkey in data:
            x=cellkey[1]
            y=cellkey[0]
            value=data[cellkey]
            if unicode(value)==u"#N/A!" or x>rejectafter:
                continue
            if y>3 and x>0 and value is not None and (not isinstance(value, str) or (value.strip()!="" and (value.strip()!="#N/A!"))):
                newrow=Row()
                newrow.date=self.globaldate
                newrow.measure=data[(2,x)]
                newrow.period=data[(y,0)]
                newrow.team=self.practiceid
                newrow.value=value
                newrow.annotation=""
                newrow.extracols=False
                newrow.rownum=y+1
                newrow.datetype='excel'
                newrow.series=self.globalseries
                builtdata.append(newrow)
        return builtdata
    def getRows(self):
        return self.alldata