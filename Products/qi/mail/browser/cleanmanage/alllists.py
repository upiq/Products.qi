from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from Products.qi.util import utils

from Globals import InitializeClass




from AccessControl import ClassSecurityInfo

class ListManager(BrowserPlusView):
    
    processFormButtons=('add', 'delete.x')
    def alllists(self):
        dbproj,dbteam=self.getDBProjectTeam()
        if dbproj is None:
            return []
        elif dbteam is None:
            return self.sortlist(dbproj.mailinglist_set.filter(team__isnull=True), utils.compareMailingLists2)
        else:  
            return self.sortlist(dbteam.mailinglist_set.all().order_by('listname'), utils.compareMailingLists2)
    
    def manageurl(self, list):
        format='%s/configurelist?listid=%s'
        return format%(self.context.absolute_url(),list.id)
    
    def makeaddress(self,list):
        format='%s+%s@%s'
        imaptool=self.context.IMapHost
        return format%(imaptool.name_part,list.listname,imaptool.source_domain)
    
    def validate(self, form):
        if 'add' in form:
            if self.requiredAvailable(DB.MailingList.objects.all(),'listname'):
                if form['listname'].find(' ')>-1:
                    self.addError('listname', 'Mailing List names may not have spaces')
            self.required('description')
    
    def action(self, form, action):
        if action=='delete.x':
            
            deleted=DB.MailingList.objects.get(id=form['listid'])
            deleted.delete()
        elif action=='add':
            created=DB.MailingList()
            created.listname=form['listname'].strip()
            created.description=form['description'].strip()
            created.project, created.team=self.getDBProjectTeam()
            created.joinable=False
            created.replyable=False
            created.save()
            self.doRedirect('configurelist?listid=%i'%created.id)
    
    def sublists(self):
        dbproj,dbteam=self.getDBProjectTeam()
        if dbproj is None:
            return []
        elif dbteam is None:
            return self.sortlist(dbproj.mailinglist_set.filter(team__isnull=False), utils.compareMailingLists2)
        else:
            result=DB.MailingList.objects.none();
            for subteam in dbteam.team_set.all():
                result=result | subteam.mailinglist_set.all()
            return self.sortlist(result,utils.compareMailingLists2)


            
InitializeClass(ListManager)