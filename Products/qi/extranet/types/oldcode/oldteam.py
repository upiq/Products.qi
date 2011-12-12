from AccessControl import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from OFS.OrderSupport import OrderSupport
from zope.component.factory import Factory
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from plone.locking.interfaces import ITTWLockable
from plone.app.content.interfaces import INameFromTitle
from plone.app.content.container import Container

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.qi import MessageFactory as _
from interfaces import ITeam
from AccessControl.Permissions import view as View

from plone.portlets.interfaces import ILocalPortletAssignable


class Team(BrowserDefaultMixin, OrderSupport, Container):
    """  QITeamspace implemenation of a project
    """
    implements(ITeam, ITTWLockable, INameFromTitle,ILocalPortletAssignable)
    security = ClassSecurityInfo()
    portal_type = "qiteam"
    title = u""
    description = u""
    groupname=None

    def __init__(self, id=None):
        super(Team, self).__init__(id)
    
    def Description(self):
        """override CMF description accessor"""
        if isinstance(self.description, unicode):
            return self.description.encode('utf-8')
        return self.description or ''
    

InitializeClass(Team)
teamFactory = Factory(Team, title=_(u"Create a new QI team"))