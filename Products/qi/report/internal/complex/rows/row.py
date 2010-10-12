from zope.component.factory import Factory
from Products.qi import MessageFactory as _
from OFS.SimpleItem import SimpleItem
from plone.app.content.container import Container

from zope.interface import implements
from interfaces import IChartRow
from Products.qi.report.internal.complex.widgits.interfaces import IWidgit

def sortreports(a,b):
    return cmp(a.column, b.column)
    
class WidgitGroup:
    def __init__(self):
        self.widgits=[]
    def add(self, widgit):
        self.widgits.append(widgit)
        

class ChartRow(Container):
    implements(IChartRow)
    rowindex=0
    idcounter=0
    def rownum(self):
        return self.rowindex
    
    def getrow(self):
        return self
    
    def groups(self):
        widgits=self.widgits()
        previous=None
        addedGroup=None
        groups=[]
        for widgit in widgits:
            if      previous is None or \
                    previous.widgitname!=widgit.widgitname or \
                    previous.widgitname!='small multiple':
                if addedGroup is not None:
                    groups.append(addedGroup)
                addedGroup=WidgitGroup()
                addedGroup.add(widgit)
            else:
                addedGroup.add(widgit)
            previous=widgit
        if addedGroup is not None:
            groups.append(addedGroup)
        return groups
    
    def widgits(self):
        return [x for x in self.getChildNodes() if IWidgit.isImplementedBy(x)]
    
    def addwidgitobject(self, widgit):
        self.idcounter+=1
        widgit.id='widgit-%i'%self.idcounter
        widgit.title=widgit.id
        self._setObject(widgit.id,widgit)
        
        
    

rowfactory=Factory(ChartRow,title="add additional row")