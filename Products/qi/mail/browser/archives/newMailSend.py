from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from Products.qi.util import utils

class MailArchives(BrowserPlusView):
    relatedPages=(  ('SendMail.html','Send mail'),
                    (None,'Mail Archives'))
    
    processFormButtons=()
    def validate(self,form):
        pass
        #meh
    def action(self, form, command):
        pass
    
    def getLists(self):
        if self.user()=="admin":
            return DB.MailingList.objects.all()
        return utils.getListsForUser(self.user(),self.context)

#handles the display of users mailing lists in archive
class MailingLists(BrowserPlusView):
    def mylists(self):
        if self.user()=="admin":
            return DB.MailingList.objects.all()
        return utils.getListsForUser(self.user(),self.context)

#handles display of threads page in archive
class Threads(BrowserPlusView):
    def getThreads(self):
        if 'id' not in self.context.request.form:
            return ()
        id=int(self.context.request.form['id'])
        return DB.MailingList.objects.get(id=id).mailthread_set.all()
        
    def firstPoster(self,thread):
        messages=thread.message_set.all().order_by('sent')
        if len(messages)>0:
            return messages[0].fromuser
        return "None"
    
    def listname(self):
        if 'id' not in self.context.request.form:
            return ()
        id=int(self.context.request.form['id'])
        return DB.MailingList.objects.get(id=id).listname
        
#handles display of messages page for archives
class Messages(BrowserPlusView):
    def getMessages(self):
        if 'id' not in self.context.request.form:
            return ()
        id=int(self.context.request.form['id'])
        return DB.MailThread.objects.get(id=id).message_set.all()
        
    def subject(self):
        if 'id' not in self.context.request.form:
            return None
        id=int(self.context.request.form['id'])
        return DB.MailThread.objects.get(id=id).subject
        
    def cleanbody(self, body):
        result=body.replace("&","&amp;")
        result=result.replace("<","&lt;")
        result=result.replace(">","&gt;")
        return result.replace("\n","<br />")

    def mailinglist(self):
        if 'id' not in self.context.request.form:
            return False
        id= int(self.context.request.form['id'])
        return DB.MailThread.objects.get(id=id).list
        
