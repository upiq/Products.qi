#primary interface
from interfaces import IQIChart
#types ant utilities used inside class
from BTrees.OOBTree import OOSet
from Products.qi import MessageFactory as _
from zope.interface import implements
#imports used outside a class
from zope.component.factory import Factory
from App.class_init import default__class_init__ as InitializeClass
#extensions
#from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from OFS.SimpleItem import SimpleItem
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from plone.app.content.interfaces import INameFromTitle
from plone.app.content.container import Container


class Chart(SimpleItem,BrowserDefaultMixin, Container):
    implements(IQIChart, INameFromTitle)
    portal_type="qichart"
    title=u"Unnamed Chart"
    description=u"Undefined"
    startdate=None
    enddate=None
    def __init__(self, id=None):
        super(Chart, self).__init__(id)
        self.measures=OOSet()
        self.teams=OOSet()
        self.derived=OOSet()
        
        

InitializeClass(Chart)
chartFactory = Factory(Chart, title=_(u"Create a new online report"))
