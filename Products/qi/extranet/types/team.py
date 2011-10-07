from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent
from App.class_init import default__class_init__ as InitializeClass
from OFS.OrderSupport import OrderSupport
from zExceptions import MethodNotAllowed
from zExceptions import NotFound
from zope.component.factory import Factory
from zope.interface import implements
from Products.qi.util.logger import logger

from Products.CMFCore.utils import getToolByName

from Products.qi.extranet.viewlets.menu.menu import MenuItem

from plone.locking.interfaces import ITTWLockable
from plone.app.content.interfaces import INameFromTitle
from plone.app.content.container import Container

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.qi import MessageFactory as _
from interfaces import IQITeam
from AccessControl.Permissions import view as View

from plone.portlets.interfaces import ILocalPortletAssignable


class Team(BrowserDefaultMixin, OrderSupport, Container):
    """  QITeamspace implemenation of a project
    """
    implements(IQITeam, ITTWLockable, INameFromTitle,ILocalPortletAssignable)
    security = ClassSecurityInfo()
    portal_type = "qiteam"
    upload_types=[]
    dbid=None
    title = u""
    description = u""
    groupname=None

    def __init__(self, id=None):
        super(Team, self).__init__(id)
        self.managers = []
        self.addable_types = []
    
    def Description(self):
        """override CMF description accessor"""
        if isinstance(self.description, unicode):
            return self.description.encode('utf-8')
        return self.description or ''
    
    baseItems=( 
        ("members.html","Manage Team Members","Modify portal content"),
        )

    otherSources=()
    
    def getMenuItems(self):
        parent=aq_parent(aq_inner(self))
        result=parent.getMenuItems()
        projectMenu=MenuItem(context=self, name="%s Tasks"%self.title)
        projectMenu.items=[]
        for item in self.baseItems:
            newitem=MenuItem(context=self,
                target=item[0], name=item[1],permission=item[2])
            if item[0]=='':
                newitem.islinked=False
            projectMenu.items.append(newitem)
                
        result.append(projectMenu)
        return result

    def getTeam(self):
        return self

    security.declareProtected(View, 'HEAD')
    def HEAD(self, REQUEST, RESPONSE):
        """ Override HEAD method for HTTP HEAD requests.

        o If the default view can't be acquired, return 404 (Not found).

        o if the default view has no HEAD method, return 405
          (Method not allowed).
        """
        view_id = self.getDefaultPage() or self.getLayout()
        if view_id is None:
            raise NotFound('No view method known for requested resource')

        view_method = getattr(self, view_id, None)
        if view_method is None:
            raise NotFound('View method %s for requested resource is not ' 
                             'available.' % view_id)

        if getattr(aq_base(view_method), 'HEAD', None) is not None:
            return view_method.__of__(self).HEAD(REQUEST, RESPONSE)

        raise MethodNotAllowed('HEAD method not supported for this resource.')

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
    def isSubTeam(self):
        parent=aq_parent(aq_inner(self))
        if parent.isTeam():
            return True
        return False
    def isTeam(self):
        return True

InitializeClass(Team)
teamFactory = Factory(Team, title=_(u"Create a new QI team"))
