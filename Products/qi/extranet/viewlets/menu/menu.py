# package

from AccessControl import getSecurityManager
import AccessControl

class MenuItem:
    
    requiredPermission=None
    name=None
    context=None
    target=None
    islinked=True
    
    def hasPermission(self):
        if self.requiredPermission is None:
            return True
        
        
            
        mtool = self.context.portal_membership
        checkPermission = mtool.checkPermission
        
        security=getSecurityManager()
        user=security.getUser()
        
        if self.requiredPermission.startswith('Role:'):
            role=self.requiredPermission[5:]
            if role in user.getRolesInContext(self.context):
                return True
            else: 
                return False
        
        # checkPermissions returns true if permission is granted
        if checkPermission(self.requiredPermission, self.context):
            return True
        else:
            return False
    def __init__(self,context=None,target="javascript:void(0)",
                name="Untitled Menu Option", permission=None):
        self.context=context
        self.target=target
        self.name=name
        self.requiredPermission=permission
        self.items=[]
    def hasChildren(self):
        return len(self.items)>0
        
    def link(self):
        format="%s/%s"
        return format%(self.context.absolute_url(),self.target)
        
