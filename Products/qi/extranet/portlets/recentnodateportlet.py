from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

# Import the base portlet module whose properties we will modify
from plone.app.portlets.portlets import recent

class IRecentNoDatePortlet(recent.IRecentPortlet):
    pass

class RecentNoDateRenderer(recent.Renderer):
    """ Overrides recent.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('recentnodateportlet.pt')

class RecentNoDateAssignment(recent.Assignment):
    """ Assigner for recentnodate portlet. """
    implements(IRecentNoDatePortlet)

    @property
    def title(self):
        return _(u"Recent Items-No Date")
class RecentNoDateAddForm(recent.AddForm):
    """ Make sure that add form creates instances of our custom portlet instead of the base class portlet. """
    def create(self, data):
        return RecentNoDateAssignment(**data)