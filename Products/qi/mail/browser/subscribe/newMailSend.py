from Products.qi.util.general import BrowserPlusView
from Products.qi.mail.newlist import Message
from Products.CMFCore.utils import getToolByName
from qi.sqladmin import models as DB
#from DateTime.DateTime import datetime
import AccessControl
from Products.qi.util import utils
#from Products.qi.extranet.pages.success import Success

class Subscribe(BrowserPlusView):
    processFormButtons=()
    def action(self, form, command):
        pass
    def validate(self, form):
        pass
    
    def getAvailableLists(self):
        currentLists=utils.getListsForUser(self.user(),self.context)
        allLists=utils.getPossibleListsForUser(self.user(),self.context)
        allLists=allLists.filter(joinable=True)
        ids=[k.id for k in currentLists]

        result= allLists.exclude(id__in=ids)
        return self.sortlist(result,utils.compareMailingLists)
    
    def getLockedLists(self):
        base=utils.getListsForUser(self.user(),self.context)
        nojoin=base.filter(joinable=False)
        ids=[]
        for mlist in base:
            if len(mlist.mailinglistsubscriber_set.filter(
                userid=self.user()))==0:
                ids.append(mlist.id)
        other=base.filter(id__in=ids)
        result= nojoin|other
        return self.sortlist(result,utils.compareMailingLists)
           
    def getRemoveableLists(self):
        currentLists=utils.getListsForUser(self.user(),self.context)
        locked=self.getLockedLists()
        ids=[k.id for k in locked]
        result= currentLists.exclude(id__in=ids)
        return self.sortlist(result,utils.compareMailingLists)        
        
    