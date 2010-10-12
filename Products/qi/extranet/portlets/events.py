from plone.app.portlets.portlets.events import Renderer as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.compress import xhtml_compress
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from DateTime.DateTime import DateTime
from Products.qi.util.general import BrowserPlusView
from AccessControl import Unauthorized

class Renderer(Base):

    _template = ViewPageTemplateFile('events.pt')

    def __init__(self, *args):
        Base.__init__(self, *args)

    def published_events(self):
        result=self._data()
        actualresults=[]
        for item in result:
            try:
                if hasattr(item.getObject(),'getProject'):
                    project =  self.context.getProject()
                    itemproject=item.getObject().getProject()
                    if(project==itemproject):
                        actualresults.append(item)
            except Unauthorized:
                pass
        return actualresults[:self.data.count]

    #again getting rid of ram cacheing 
    def render(self):
        return xhtml_compress(self._template())
    
    def all_events_link(self):
        format='%s/%s'
        return format%(self.context.getProject().absolute_url(),
            'project_events.html')
        
    def _data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        limit = self.data.count
        state = self.data.state
        return catalog(portal_type='Event',
                       review_state=state,
                       end={'query': DateTime(),
                            'range': 'min'},
                       sort_on='start')
                       
class ProjectEvents(BrowserPlusView):
    processFormButtons=()