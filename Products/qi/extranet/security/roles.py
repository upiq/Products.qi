from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

from Products.CMFPlone import PloneMessageFactory as _

# These are for everyone

class QICRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_can_enter_data", default=u"Can enter data")
    required_permission = None
