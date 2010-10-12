from Products.Five.browser import BrowserView
import AccessControl
from DateTime import DateTime
from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet

class UserTracker(BrowserView):
    
    def __call__(self, *args, **kwargs):
        self.updateUser()
        return ""
        
    def updateUser(self):
        time = DateTime()
        mp = self.context.acl_users.mutable_properties
       
        sec=AccessControl.getSecurityManager()
        user=sec.getUser()

        props = mp.getPropertiesForUser(user)
        props.setProperty(user, 'last_activity', time)