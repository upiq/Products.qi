from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent
from App.class_init import default__class_init__ as InitializeClass
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
        self.managers = []
    
    def Description(self):
        """override CMF description accessor"""
        if isinstance(self.description, unicode):
            return self.description.encode('utf-8')
        return self.description or ''
    
    baseItems=( 
        ("members.html","Manage Team Members","Modify portal content"),
        )

    otherSources=()
    
    def getTeam(self):
        return self

    def getTeamUsers(self, groupname='members'):
        group=self.getGroup(groupname)
        plugin = self.acl_users.source_groups
        return [x[0] for x in plugin.listAssignedPrincipals(group)]
    
    def getGroup(self, groupname="members"):
        return self.getTeamGroup(groupname)
    
    def getTeamGroup(self, groupname="members"):
        #exercise the project's ability to identify it's own name as necessary
        projectgroup=self.getProjectGroup()
        team_id= self.getId()
        if self.groupname is None:
            #we haven't had a chance like this yet
            self.groupname=team_id
        project=self.getProject()
        group='%s-%s-%s' %(project.groupname,self.groupname,groupname)
        return group


InitializeClass(Team)
teamFactory = Factory(Team, title=_(u"Create a new QI team"))
