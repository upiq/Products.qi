from Products.qi.util.general import BrowserPlusView
from Products.qi.mail.mailinglist import MailBatch
from Products.CMFCore.utils import getToolByName
from qi.sqladmin import models as DB
from DateTime.DateTime import datetime
from Products.qi.util import utils
import AccessControl

class ManageLists(BrowserPlusView):
    processFormButtons=("delete",)
    
    def getCurrentLists(self):
        result=self.localLists()
        return self.sortlist(result,utils.compareMailingLists)
    
    def localLists(self):
        #use browser+ssss
        dbproj,dbteam=self.getDBProjectTeam()
        if not dbproj:
            #later make this global lists
            return DB.MailingList.objects.filter(project__isnull=True, 
                                                 team__isnull=True)
        projectLists=dbproj.mailinglist_set.all()
        if dbteam:
            result=projectLists.filter(team__id=dbteam.id)
        else:
            result=projectLists.filter(team__isnull=True)
        return result
    
    def validate(self, form):
        self.requiredInTable(self.localLists(),
                "deleted","The deleted mailing list")
    
    def action(self,form, action):
        id=int(form['deleted'])
        deleted=self.localLists().filter(id=id)
        deleted.delete()