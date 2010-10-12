from Products.qi.util.general import BrowserPlusView
from Products.qi.mail.mailinglist import MailBatch
from Products.CMFCore.utils import getToolByName
from qi.sqladmin import models as DB
from DateTime.DateTime import datetime
import AccessControl
from Products.qi.extranet.pages.success import Success

class SendLink(BrowserPlusView):
    processFormButtons=('send',)
    
    def validate(self, form):
        if self.requiredInForm('email'):
            if form['email']!='admin':
                self.requiredEmail('email')
        self.requiredInForm('comment')
        if not self.hasUsers():
            self.addError('base', """There are no users for this project
 or team.  If you attempt to send an email, none will be sent.
 Please add users to your project or team and send this message again or
 contact your project manager or team lead to add users.""")

    def action(self, form, action):
        batch=MailBatch()
        messageformat="""File from %s 
User comment:%s
Link to %s:
%s"""
        user=form['email']
        comment=form['comment']
        objecturl=self.context.absolute_url()
        messagebody=messageformat%(user,comment,self.context.title, objecturl)
        member_ids=self.context.getProjectUsers('members')
        subject="QI Teamspace file"
        batch.prepare(messagebody, member_ids,subject,self.context, user)
        batch.sendMessages()
        saved=DB.MailArchive()
        saved.body=messagebody
        saved.restriction=0
        saved.sent=datetime.now()
        saved.subject=subject
        saved.fromuser=user
        saved.project=self.context.getDBProject()
        #saved.team=self.context.getDBTeam()
        saved.save()
        self.doRedirect('mail_success.html')
    
    def hasUsers(self):
        users=self.context.getProjectUsers()
        return len(users)>0
    
class SendTeamLink(SendLink):
    def action(self, form, action):
        batch=MailBatch()
        messageformat="""File from %s 
User comment:%s
Link to %s:
%s"""
        user=form['email']
        comment=form['comment']
        objecturl=self.context.absolute_url()
        messagebody=messageformat%(user,comment,self.context.title, objecturl)
        member_ids=self.context.getTeamUsers('members')
        subject='QI Teamspace file'
        batch.prepare(messagebody, member_ids,subject,self.context, user)
        batch.sendMessages()
        saved=DB.MailArchive()
        saved.body=messagebody
        saved.restriction=0
        saved.sent=datetime.now()
        saved.subject=subject
        saved.fromuser=user
        saved.project=self.context.getDBProject()
        saved.team=self.context.getDBTeam()
        saved.save()
        self.doRedirect('mail_success.html')
        
    def hasUsers(self):
        users=self.context.getTeamUsers()
        return len(users)>0
    

class LinkSuccess(Success):
    def target(self):
        return '%s/%s'%(self.context.absolute_url(),'/')
        
    def verb(self):
        return ''
        