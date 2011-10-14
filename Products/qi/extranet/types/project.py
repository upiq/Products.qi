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
from interfaces import IProject
from AccessControl.Permissions import view as View

from plone.portlets.interfaces import ILocalPortletAssignable


class Project(BrowserDefaultMixin, OrderSupport, Container):
    """  QITeamspace implemenation of a project
    """
    implements(IProject, ITTWLockable, INameFromTitle, ILocalPortletAssignable)
    security = ClassSecurityInfo()
    portal_type = "qiproject"
    description = u""
    groupname=None

    def __init__(self, id=None):
        super(Project, self).__init__(id)
        self.managers = []
        self.logo = ''


InitializeClass(Project)

projectFactory = Factory(Project, title=_(u"Create a new QI project"))

