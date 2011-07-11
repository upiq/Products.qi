from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner, aq_parent
from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
from Products.qi.util.general import BrowserPlusView

def lcmp(c1,c2):
    return cmp(c1.getProperty('fullname').lower(),c2.getProperty('fullname').lower())

class UserList(BrowserPlusView):
    
    def getUserList(self):
        acl = getToolByName(self.context,'acl_users')
        if self.context.isTeam():
            uids = self.context.getTeamUsers()
        else:
            uids = self.context.getProjectUsers()
        
        return sorted([acl.getUserById(x) for x in uids], lcmp)
        
    def getUserListTitle(self):
        
        header = "Member List: "
        if self.context.isTeam():
            header += "%s" % self.context.getTeam().title
        else:
            header += "All Project Members"
        return header
        
    def upperTeam(self):
        parent = aq_parent(aq_inner(self.context))
        return parent.title
        
    def getLogo(self):
        if hasattr(self.context, "project_logo.jpg"):
            return getattr(self.context, "project_logo.jpg").absolute_url()
        else:
            return None
