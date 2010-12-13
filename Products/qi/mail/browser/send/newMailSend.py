from Products.qi.util.general import BrowserPlusView
from Products.qi.mail.newlist import Message
from Products.CMFCore.utils import getToolByName
from qi.sqladmin import models as DB
#from DateTime.DateTime import datetime
import AccessControl
from Products.qi.util import utils
from Products.qi.extranet.pages.success import Success

class MailForm(BrowserPlusView):
    

    
    processFormButtons=('send',)
    
    def validate(self, form):
        inlist=False
        for x in self.availableMailingLists():
            if x.id==int(form['list']):
                inlist=True
        if inlist:
            dblist=self.getList()
            context=self.context
            project, team=self.getProjectTeam()
            if not self.hasUsers():
                users=utils.getUsersForMailingList(dblist, context)
                if len(users)==0:
                    self.addError('list',
"""There are no users for selected list.
If you attempt to send a message, no email will be sent.
Please add recipients to the mailing list and send this message again or
contact your project manager or team lead to add recipients.""")
        else:
            self.addError('base','The information you submitted is invalid')
        if self.required('email'):
            if form['email'] == 'admin':
                pass
            else:
                self.requiredEmail('email')
            
        self.required('subject', 'Subject')
        if self.required('body','Message Body'):
            body=form['body']
            for c in body:
                if ord(c) not in range(128):
                    self.addError('body',"""
The message body contained an unrecognized symbol or letter: "%s".
Please resend the message from your email client instead.
"""%c)
                    break;
        
        
    
    def hasUsers(self):
        print 'checking users'
        list=self.getList()
        project, team=self.getProjectTeam()
        return len(utils.getUsersForMailingList(list, self.context))>0
    
    def action(self, form, action):
        dblist=self.getList()
        message=Message()
        message.subject=form['subject']
        fromemail=self.email()
        if fromemail=="":
            fromemail=form['email']
        message.fromemail=fromemail
        message.contents=form['body']
        message.sendAll(dblist, self.context)
        message.save(dblist,False)
        self.doRedirect('mail_success.html')
    
    def generalUpdate(self):
        pass
    
        
    def availableMailingLists(self):
        s = utils.getListsForUser(str(self.user()), self.context)
        return self.sortlist(s, utils.compareMailingLists2)
        
    def defaultlistserv(self):
        return -1
        
    def getList(self):
        form=self.request.form
        listid=int(form['list'])
        return DB.MailingList.objects.get(id=listid)
        
        
class NotifyForm(MailForm):
    def validate(self, form):
        inlist=False
        for x in self.availableMailingLists():
            if x.id==int(form['list']):
                inlist=True
        if inlist:
            dblist=self.getList()
            context=self.context
            project, team=self.getProjectTeam()
            if not self.hasUsers():
                users=getUsersForMailingList(dblist, context)
                if len(users)==0:
                    self.addError('list',
"""There are no users for selected list.
If you attempt to send a message, no email will be sent.
Please add recipients to the mailing list and send this message again or
contact your project manager or team lead to add recipients.""")
        else:
            self.addError('base','The information you submitted is invalid')
        if self.required('email'):
            if form['email'] == 'admin':
                pass
            else:
                self.requiredEmail('email')

            
        #self.required('subject', 'Subject')
        self.required('body','Message Comment')

    bodyformat="""%s
This is a notification about content which can be accessed at %s"""
    def availableMailingLists(self):
        s = utils.getListsForUser(str(self.user()), self.context)
        return self.sortlist(s, utils.compareMailingLists2)
    
    def action(self, form, action):
        dblist=self.getList()
        message=Message()
        message.subject="Site content notification: %s"%self.context.title
        fromemail=self.email()
        if fromemail=="":
            fromemail=form['email']
        message.fromemail=fromemail
        message.contents=self.bodyformat%(form['body'],
            self.context.absolute_url())
        message.sendAll(dblist, self.context)
        message.save(dblist,False)
        self.doRedirect('mail_success.html')
    
        
class MailSuccess(Success):
    def target(self):
        return '%s/%s'%(self.context.absolute_url(),'newsend.html')
        
    def verb(self):
        return 'send another email'
        