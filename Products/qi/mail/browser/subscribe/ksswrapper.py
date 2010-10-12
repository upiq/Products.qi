from Products.qi.util.general import BrowserPlusView
from kss.core.ttwapi import startKSSCommands
from kss.core.ttwapi import getKSSCommandSet
from kss.core.ttwapi import renderKSSCommands
from qi.sqladmin import models as DB
from Products.qi.util import utils
import re
import AccessControl
from Products.qi.util.ksswrapper import KSSAction, KSSHtmlRenderer
from Products.qi.util.ksswrapper import KSSInnerWrapper, KSSReplaceWrapper
from Products.qi.util.ksswrapper import KSSAddWrapper, SimpleResponse
class UnSubscribe(KSSAction):

    def doKss(self, core):
        listid=int(self.context.request.form['listid'])
        dbuser=DB.MailingListSubscriber.objects.filter(list__id=listid,
            userid=self.user())
        dbuser.delete()
        
class Subscribe(KSSAction):
    def doKss(self, core):
        listid=int(self.context.request.form['listid'])
        dbuser=DB.MailingListSubscriber()
        dbuser.list=DB.MailingList.objects.get(id=listid)
        dbuser.userid=self.user()
        dbuser.save()

class UpdateSubscribe(KSSReplaceWrapper):
    def getTarget(self):
        return 'listbody'
    
    # x>0 means right is first

    
    def getAvailableLists(self):
        currentLists=utils.getListsForUser(self.user(),self.context)
        allLists=utils.getPossibleListsForUser(self.user(),self.context)
        allLists=allLists.filter(joinable=True)
        ids=[k.id for k in currentLists]

        result= allLists.exclude(id__in=ids)
        print result
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
        
    def user(self):
        sec=AccessControl.getSecurityManager()
        user=sec.getUser()
        return str(user)
    
