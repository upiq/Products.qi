from plone.app.portlets.portlets.news import Renderer as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.compress import xhtml_compress
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from DateTime.DateTime import DateTime
from AccessControl import Unauthorized

class Renderer(Base):

    _template = ViewPageTemplateFile('news.pt')

    def __init__(self, *args):
        Base.__init__(self, *args)
        self.updated=False

    def published_news_items(self):
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
                #don't have local permissions to check the object's project
                #this is likely a result of it being out of our list of acceptable items
                pass
                
        self.initializing=True
        return actualresults[:self.data.count]

    #just to get rid of the cachekey
    def render(self):
        return xhtml_compress(self._template())
    
    def all_news_link(self):
        format='%s/%s'
        return format%(self.context.getProject().absolute_url(),
            'project_news.html')
        
    def _data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        limit = self.data.count
        state = self.data.state
        return catalog(portal_type='News Item',
                       review_state=state,
                       sort_on='Date',
                       sort_order='reverse')
