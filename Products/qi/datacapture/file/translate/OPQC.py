from Products.qi.datacapture.file.translate.square import SquareTranslator, Column
from datetime import date
from Products.qi.datacapture.file.uploads.uploadutils import fromExcelDate



class MaintenanceTranslator(SquareTranslator):
    def extractCols(self):
        self.IDCol=None
        self.FacIDCol=None
        self.bundleCol=None
        self.NotesCol=None
        titles=[x.title for x in self.columns.values()]
        newcols=[]
        for columnnum in self.columns:
            column=self.columns[columnnum]
            if column.title.lower()=="id":
                self.IDCol=column
            elif column.title.lower()=="facid":
                self.FacIDCol=column
            elif column.title.lower()=="maint bundle date":
                self.bundleCol=column
            elif column.title.lower()=="title":
                self.NotesCol=column
            else:
                newcols.append(column)
        self.columns=newcols
    def buildPeriods(self):
        dateCol=Column()
        self.reportingDate=date.today()
        dateCol.title="Reporting Period"
        dateCol.data=[None for x in range(len(self.bundleCol.data))]
        for x in range(len(self.bundleCol.data)):
            datestring=self.bundleCol.data[x]
            if datestring:
                resultdate=fromExcelDate(datestring)
            else:
                resultdate=None
            dateCol.data[x]=resultdate
        self.dateCol=dateCol