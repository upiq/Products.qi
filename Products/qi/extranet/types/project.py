from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import default__class_init__ as InitializeClass
from BTrees.OOBTree import OOSet
from OFS.OrderSupport import OrderSupport
from zExceptions import MethodNotAllowed
from zExceptions import NotFound
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
    
    def getProject(self):
        return self
    
    def getProjectUsers(self, groupname='members'):
        group=self.getProjectGroup(groupname)
        acl_users = getToolByName(self, 'acl_users')
        plugin = acl_users.source_groups
        return [x[0] for x in plugin.listAssignedPrincipals(group)]
    
    def getGroup(self, groupname="members"):
        return self.getProjectGroup(groupname)
    
    def getProjectGroup(self, groupname="members"):
        project_id = self.getId()
        if self.groupname is None:
            self.groupname=project_id
        group='%s-%s' %(self.groupname,groupname)
        return group


InitializeClass(Project)

projectFactory = Factory(Project, title=_(u"Create a new QI project"))

