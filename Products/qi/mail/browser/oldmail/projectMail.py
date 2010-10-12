from Products.qi.util.general import BrowserPlusView
from Products.qi.mail.mailinglist import MailBatch
from Products.CMFCore.utils import getToolByName
from qi.sqladmin import models as DB
from DateTime.DateTime import datetime
import AccessControl
from Products.qi.extranet.pages.success import Success

class MailForm(BrowserPlusView):
    
    relatedPages=(  (None,'Send mail'),
                    ('MailArchives.html','Mail Archives'))

    
    processFormButtons=('send',)
    
    def validate(self, form):
        if not self.hasUsers():
            self.addError('base',"""There are no users for this project or team.
If you attempt to send an email, none will be sent.
Please add users to your project or team and send this message again or
contact your project manager or team lead to add users.""")
        if self.required('email'):
            if form['email'] == 'admin':
                pass
            else:
                self.requiredEmail('email')
            
        self.required('subject', 'Subject')
        self.required('body','Message Body')
        
        
    
    def action(self, form, action):
        messages=MailBatch()
        text=form['body']
        sender=form['email']
        subject=form['subject']
        
        
        #project_id = self.context.getId()
        group=self.context.getProjectGroup()
        mtool = getToolByName(self.context, 'portal_membership')
        plugin = self.context.acl_users.source_groups
        member_ids=[x[0] for x in plugin.listAssignedPrincipals(group)]
        messages.prepare(text,member_ids,subject,self.context,sender)
        messages.sendMessages()
        archive=DB.MailArchive()
        archive.project=self.context.getDBProject()
        archive.team=None #just being explicit
        archive.restriction=0
        archive.fromuser=sender
        archive.subject=subject.strip()
        archive.sent=datetime.now()
        archive.body=text
        archive.save()
        self.doRedirect('mail_success.html')     
    
    def generalUpdate(self):
        pass
    
    def hasUsers(self):
        users=self.getUsers()
        return len(users)>0
        
    def getUsers(self):
        project_id = self.context.getId()
        group=self.context.getProjectGroup()
        mtool = getToolByName(self.context, 'portal_membership')
        plugin = self.context.acl_users.source_groups
        return [x[0] for x in plugin.listAssignedPrincipals(group)]
        
class TeamMailForm(MailForm):
    def action(self, form, action):
        messages=MailBatch()
        text=form['body']
        sender=form['email']
        subject=form['subject']
        
        

        group=self.context.getGroup()
        mtool = getToolByName(self.context, 'portal_membership')
        plugin = self.context.acl_users.source_groups
        member_ids=[x[0] for x in plugin.listAssignedPrincipals(group)]
        messages.prepare(text,member_ids,subject,self.context,sender)
        messages.sendMessages()
        archive=DB.MailArchive()
        archive.project=self.context.getDBProject()
        archive.team=self.context.getDBTeam()
        archive.fromuser=sender
        archive.subject=subject.strip()
        archive.restriction=0
        archive.sent=datetime.now()
        archive.body=text
        archive.save()
        self.doRedirect('mail_success.html')
        
    def getUsers(self):
        group=self.context.getGroup()
        mtool = getToolByName(self.context, 'portal_membership')
        plugin = self.context.acl_users.source_groups
        return [x[0] for x in plugin.listAssignedPrincipals(group)]
        
        
class MailArchives(BrowserPlusView):
    relatedPages=(  ('SendMail.html','Send mail'),
                    (None,'Mail Archives'))
                    
    processFormButtons=()
    def validate(self,form):
        pass
        #meh
    def action(self, form, command):
        pass
        
    def buildRestriction(self, member):
        sec=AccessControl.getSecurityManager()
        user=sec.getUser()

        if user.allowed('Manager'):
            return 2
        
        return 0
        
    
    def getHistory(self, member):
        return ()
        
    def getProjectTeam(self):
        return None, None
        
    def parsebody(self, emailbody):
        chunks=emailbody.split('\n')
        result=""
        for chunk in chunks:
            result+=chunk+"<br />"
        return result
        
class ProjectArchives(MailArchives):
    def getHistory(self, member):
        dbproj=self.context.getDBProject()
        source=DB.MailArchive.objects
        result=source.filter(  project=dbproj,
                        team__isnull=True,
                        restriction__lte=self.buildRestriction(member),
                        parent__isnull=True
                        )
        return result
        
    def getProjectTeam(self):
        return self.context.getProject(), None

class TeamArchives(MailArchives):
    def getHistory(self, member):
        dbteam=self.context.getDBTeam()
        dbproj=self.context.getDBProject()
        source=dbteam.mailarchive_set
        
        result=source.filter(
                        restriction__lte=self.buildRestriction(member),
                        parent__isnull=True).order_by('sent')
        return result
        
    def getProjectTeam(self):
        team=self.context.getTeam()
        project=self.context.getProject()
        return project, team
        
        
class MailSuccess(Success):
    def target(self):
        return '%s/%s'%(self.context.absolute_url(),'newsend.html')
        
    def verb(self):
        return 'send another email'
        
class SetupGroups(BrowserPlusView):
    processFormButtons=('add',)
    def validate(self, form):
        self.required('added')
    def action(self, form, action):
        added=DB.SpecialMailGroup()
        added.groupname=form['added']
        added.save()
    
       
        