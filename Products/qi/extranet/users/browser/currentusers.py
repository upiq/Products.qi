from Products.CMFCore.utils import getToolByName
import AccessControl
from Products.qi.util.general import BrowserPlusView
from Products.qi.util.formvalidation import Validator
from Products.Five.browser import BrowserView
from DateTime import DateTime






class CurrentUsers(BrowserPlusView):
    
    
    def displayCurrentUsers(self):
        #figure out how to search with a conditon as the parameter
        pass
        
    def displayCurrentUsersBrute(self):
        time = DateTime()

        acl = self.context.acl_users
        output = []
        for user in acl.getUsers(): #for every user, get their last activity
            props = acl.mutable_properties.getPropertiesForUser(user).propertyItems()

            lact = dict([(m[0],m[1]) for m in props]).get('last_activity', '')

            if lact is not '':
                curtime = DateTime(lact)
            
            if(time - curtime <= .01): #this will give us a time around 15 minutes.
                output.append(user)
            
        return output
        
        
        
        
