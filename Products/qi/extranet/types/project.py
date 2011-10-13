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

from Products.qi.extranet.viewlets.menu.menu import MenuItem

from plone.locking.interfaces import ITTWLockable
from plone.app.content.interfaces import INameFromTitle
from plone.app.content.container import Container

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.qi import MessageFactory as _
from interfaces import IQIProject
from AccessControl.Permissions import view as View

from plone.portlets.interfaces import ILocalPortletAssignable


class Project(BrowserDefaultMixin, OrderSupport, Container):
    """  QITeamspace implemenation of a project
    """
    implements(IQIProject, ITTWLockable, INameFromTitle, ILocalPortletAssignable)
    security = ClassSecurityInfo()
    portal_type = "qiproject"
    dbid=None
    title = u""
    description = u""
    hideinactiveteams = False
    UploadTypes=[]
    projectTheme='Sunburst Theme'
    groupname=None

    def __init__(self, id=None):
        super(Project, self).__init__(id)
        self.managers = []
        self.addable_types = OOSet()
        self.logo = ''
    
    def getProject(self):
        return self
    
    def getUploadTypes(self):
        if not self.UploadTypes:
            self.UploadTypes=[]
        return self.UploadTypes
    
    def deleteTypes(self,types):
        for t in types:
            self.UploadTypes.remove(t)
    
    def addType(self,uploadType):
        self.UploadTypes.append(uploadType)
    
    # fixed project-level menu items: 
    baseItems=(
        ("members.html","Manage Project Members","Modify portal content"),
        )
    
    otherSources=()
    
    def getMenuItems(self):
        result=[]
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
        
    def isSubTeam(self):
        return False
    
    def isTeam(self):
        return False
        

InitializeClass(Project)

projectFactory = Factory(Project, title=_(u"Create a new QI project"))

