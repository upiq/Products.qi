from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

# Import the base portlet module whose properties we will modify
from plone.app.portlets.portlets import news

class INewsNoDatePortlet(news.INewsPortlet):
    pass

class NewsNoDateRenderer(news.Renderer):
    """ Overrides news.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('newsnodateportlet.pt')

class NewsNoDateAssignment(news.Assignment):
    """ Assigner for newsnodate portlet. """
    implements(INewsNoDatePortlet)
    
    @property
    def title(self):
        return _(u"News-No Date")

class NewsNoDateAddForm(news.AddForm):
    """ Make sure that add form creates instances of our custom portlet instead of the base class portlet. """
    def create(self, data):
        return NewsNoDateAssignment(**data)