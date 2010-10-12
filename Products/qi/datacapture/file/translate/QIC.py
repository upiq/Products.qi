from Products.qi.datacapture.file.translate.default import PracticeTranslator
from Products.qi.datacapture.file.uploads.Row import Row
from Products.qi.datacapture.file.uploads.uploadutils import makeExcel

class QICTranslator(PracticeTranslator):
    
    def loadCol(self, row, colnumber, value):
        if colnumber>5:
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
            
            
            