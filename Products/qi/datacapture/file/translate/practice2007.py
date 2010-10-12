from abstract import FileTranslator
from xlrd import *
from Products.qi.datacapture.file.uploads.Row import Row
from datetime import date

"""
#this is convenience stuff for running this in the console
from Products.qi.datacapture.file.translate.practice2007 import Practice2007Importer as p
trans=p()
import xlrd
filename='/Users/acline/Documents/Firefox downloads/Buckingham Jan 2009 tpop.xls'
testbook=xlrd.open_workbook(filename)
trans.loadData(filename)
"""

class Practice2007Importer(FileTranslator):
    def loadData(self, filename):
        self.errors={}
        self.resultrows=[]
        workbook=open_workbook(filename)
        general=self.findsheet('setup',workbook)
        dm=self.findsheet('dm_data',workbook)
        asthma=self.findsheet('asthma_data',workbook)
        self.globaldate=date.today()
        self.loadPracticeInfo(general)
        self.loadsheet(dm, 24)
        self.loadsheet(asthma, 12)
        
    def findsheet(self, sheetname, workbook):
        sheetnames=workbook.sheet_names()
        for x in sheetnames:
            if x.lower().find(sheetname)>-1:
                return workbook.sheet_by_name(x)
        self.errors[-1]=['Could not find sheet %s'%sheetname]
        

    def loadPracticeInfo(self,sheet):
        self.series=sheet.cell(7,2).value
        self.practiceid=sheet.cell(6,2).value
    
    def getErrors(self):
        return self.errors
    
    def loadsheet(self, sheet, celllimit):
        if sheet is None:
            return
        dates=sheet.col(0)
        for colnum in range(1,celllimit):
            cells=sheet.col(colnum)
            rownum=0
            measure=cells[2].value

            for cell in cells:
                dateinfo=dates[rownum].value
                rownum+=1
                if rownum<5 or cell.ctype==0:
                    pass
                else:
                    added=Row()
                    added.date=self.globaldate
                    added.measure=measure
                    added.period=dateinfo
                    added.datetype='excel'
                    added.team=self.practiceid
                    added.value=cell.value
                    added.series=self.series
                    added.annotation=""
                    added.extracols=False
                    added.rownum=rownum
                    self.resultrows.append(added)
    def getRows(self):
        return self.resultrows
    
    def extensionType(self):
        return 'xls'