from Products.qi.util.general import BrowserPlusView
from Products.qi.util.utils import getProjectsAndTeamsForUser, getListsForUser
from DateTime import DateTime
from Products.qi.extranet.types.project import Project


class MyTeamspace(BrowserPlusView):
    def teams(self):


        return getProjectsAndTeamsForUser(self.user(),self.context.qiteamspace)[1]
    def projects(self):
        return getProjectsAndTeamsForUser(self.user(),self.context.qiteamspace)[0]
    def lists(self):
        return getListsForUser(self.user(), self.context)
        
    def otherUsers(self):
        online = set()
        projs = self.projects()
        for p in projs:
            users = p.getProjectUsers()
            for user in users:
                if self.isUserOnline(user) and user != self.user():
                    online.add(user)
        
        return online
        
    def isUserOnline(self, user):
        time = DateTime()
        acl = self.context.acl_users
        user = acl.getUserById(user)
        props = acl.mutable_properties.getPropertiesForUser(user).propertyItems() #gets user property sheet
        lact = dict(props).get('last_activity', '') # '' if property absent
        if lact is not '':
            curtime = DateTime(lact)
            if(time - curtime <= .01): #any activity within the last 15 mins?
                return True

        return False
