from qi.sqladmin import models as DB
from Products.qi.browser.ksswrapper import * 

class GetThreads(KSSReplaceWrapper):
    def getTarget(self):
        return 'threads'
        
    def threads(self):
        listid=int(self.context.request.form['listid'])
        result= DB.MailingList.objects.get(id=listid).mailthread_set.all()
        return result

class EmptyMessages(KSSReplaceWrapper):
    def getTarget(self):
        return 'messages'
    
    def buildHtml(self):
        return """<td id="messages">&nbsp</td>"""

class GetMessages(KSSReplaceWrapper):
    def getTarget(self):
        return 'messages'
        
    def getMessages(self):
        threadid=int(self.context.request.form['threadid'])
        return DB.Message.objects.filter(thread__id=threadid)
        
    def cleanbody(self, body):
        result=body.replace("&","&amp;")
        result=result.replace("<","&lt;")
        result=result.replace(">","&gt;")
        return result.replace("\n","<br />")
        
                