from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _


# Import the base portlet module whose properties we will modify
from plone.app.portlets.portlets import events

class IEventNoDatePortlet(events.IEventsPortlet):
    pass

class EventNoDateRenderer(events.Renderer):
    """ Overrides events.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('eventnodateportlet.pt')

class EventNoDateAssignment(events.Assignment):
    """ Assigner for eventnodate portlet. """
    implements(IEventNoDatePortlet)
    
    @property
    def title(self):
        return _(u"Events-No Date")

class EventNoDateAddForm(events.AddForm):
    """ Make sure that add form creates instances of our custom portlet instead of the base class portlet. """
    def create(self, data):
        return EventNoDateAssignment(**data)