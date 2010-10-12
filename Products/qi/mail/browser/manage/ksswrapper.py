from Products.qi.util.general import BrowserPlusView
from kss.core.ttwapi import startKSSCommands
from kss.core.ttwapi import getKSSCommandSet
from kss.core.ttwapi import renderKSSCommands
from qi.sqladmin import models as DB
from Products.qi.util import utils
import re
from time import sleep
import AccessControl
from Products.qi.browser.ksswrapper import KSSAction, KSSHtmlRenderer
from Products.qi.browser.ksswrapper import KSSInnerWrapper, KSSReplaceWrapper
from Products.qi.browser.ksswrapper import KSSAddWrapper, SimpleResponse
from Products.CMFCore.utils import getToolByName

        
class AddGroup(KSSAction):
    def validate(self):
        self.requiredInForm('groupids')
        self.requiredInForm('listid')
    def doKss(self, core):
        #not to create any actual kss
        listid=int(self.context.request.form['listid'])
        groupidsvar=self.context.request.form['groupids']
        if type(groupidsvar) is not list:
            groupidsvar=[groupidsvar]
        groupids=[int(k) for k in groupidsvar]
        for groupid in groupids:
            maillist=DB.MailingList.objects.get(id=listid)
            group=DB.SpecialMailGroup.objects.get(id=groupid)
            maillist.groups.add(group)

class RemoveGroup(KSSAction):
    def validate(self):
        self.requiredInForm('groupids')
        self.requiredInForm('listid')
    def doKss(self, core):
        #not to create any actual kss
        listid=int(self.context.request.form['listid'])
        groupidsvar=self.context.request.form['groupids']
        if type(groupidsvar) is not list:
            groupidsvar=[groupidsvar]
        groupids=[int(k) for k in groupidsvar]
        for groupid in groupids:
            maillist=DB.MailingList.objects.get(id=listid)
            group=DB.SpecialMailGroup.objects.get(id=groupid)
            maillist.groups.remove(group)

        
class AddUsers(KSSAction):
    
    def condition(self):
        return 'addmembers' in self.context.request.form
    
    def doKss(self, core):
        #not to create any actual kss
        listid=int(self.context.request.form['listid'])
        usersadded=self.context.request.form['addmembers']
        maillist=DB.MailingList.objects.get(id=listid)
        for user in usersadded:
            dbuser=DB.MailingListSubscriber()
            dbuser.userid=user
            dbuser.list=maillist
            dbuser.save()
        
class RemoveUsers(KSSAction):
    def condition(self):
        return 'removemembers' in self.context.request.form

    def doKss(self, core):
        #not to create any actual kss
        listid=int(self.context.request.form['listid'])
        usersremoved=self.context.request.form['removemembers']
        dbusers=DB.MailingListSubscriber.objects.filter(list__id=listid
                ,userid__in=usersremoved)
        for dbuser in dbusers:
            dbuser.delete()
            
            
class AddTeams(KSSAction):
    
    def condition(self):
        return 'addteams' in self.context.request.form
    
    def doKss(self, core):
        #not to create any actual kss
        listid=int(self.context.request.form['listid'])
        teamsadded=self.context.request.form['addteams']
        dbteams=DB.Team.objects.filter(id__in=teamsadded)
        maillist=DB.MailingList.objects.get(id=listid)
        for dbteam in dbteams:
            maillist.teams.add(dbteam)
        
class RemoveTeams(KSSAction):
    def condition(self):
        return 'removeteams' in self.context.request.form

    def doKss(self, core):
        #not to create any actual kss
        listid=int(self.context.request.form['listid'])
        teamsremoved=self.context.request.form['removeteams']
        dblist=DB.MailingList.objects.get(id=listid)
        dbteams=dblist.teams.filter(id__in=teamsremoved)
        for dbteam in dbteams:
            dblist.teams.remove(dbteam)

class SetDescription(KSSAction):
    def condition(self):
        return 'description' in self.context.request.form

    def doKss(self, core):
        #not to create any actual kss
        listid=int(self.context.request.form['listid'])
        description=self.context.request.form['description']
        dblist=DB.MailingList.objects.get(id=listid)
        dblist.description=description
        dblist.save()

class UpdateList(KSSAction):
    def doKss(self, core):
        #not to create any actual kss
        listid=int(self.context.request.form['listid'])
        dblist=DB.MailingList.objects.get(id=listid)
        form=self.context.request.form
        dblist.replyable= 'replyable' in form
        dblist.joinable= 'joinable' in form
        dblist.save()

class AddList(KSSAddWrapper):
    
    def validate(self):
        if self.requiredAvailable(DB.MailingList.objects,'listname','listname',
            'mailing list name'):
            listname=self.context.request.form['listname']
            self.validateListname(listname)
        self.required('description')
        
    def validateListname(self, listname):
        expression=re.compile('^[a-zA-Z1-9-]+$')
        if not expression.match(listname):
            self.addError('listname',"""
A mailing list name may only contain letters, numbers, and dashes (no spaces or
special characters).
""")
    
    def addedlist(self):
        added=DB.MailingList()
        #later get this from a form
        dbproj,dbteam=self.getDBProjectTeam()
        added.project=dbproj
        added.team=dbteam
        added.listname=self.context.request.form['listname']
        added.joinable=False
        added.replyable=True
        added.description=self.context.request.form['description']
        added.save()
        self.addedid=added.id
        return added
        
    def customKss(self, core):
        pass
        
    def getTarget(self):
        return 'listpanel'      

class ChangeExpansionState(KSSAction):
    def doKss(self,core):
        currentvalue=int(self.context.request.form['expanded'])
        if currentvalue==0:
            currentvalue=1
        else:
            currentvalue=0
        target=self.context.request.form['target']
        
        target='#%s-expanded'%target
        core.setAttribute(target,"value",str(currentvalue))

class ShowMembers(KSSReplaceWrapper):

    def delay(self):
        return True
    def viewedlist(self):
        listid=int(self.context.request.form['listid'])
        dblist=DB.MailingList.objects.get(id=listid)
        return dblist

    def availableGroups(self):

        basequery=DB.SpecialMailGroup.objects
        viewed=self.viewedlist()
        ids=[x.id for x in viewed.groups.all()]
        notpresent=basequery.exclude(id__in=ids)
        notpresent=notpresent.filter(groupname__in=self.getLegalTargets())
        return notpresent
    def getLegalTargets(self):
        proj, team=self.getProjectTeam()
        if team:
            return ('members','leads')
        if proj:
            return ('members', 'leads', 'managers','faculty','contributors')
        return ('managers',)

    def subscribedMembers(self):
        viewed=self.viewedlist()
        mtool = getToolByName(self.context, 'portal_membership')
        users=viewed.mailinglistsubscriber_set.all().order_by('userid')
        return [{'id':x.userid ,'name': \
                 mtool.getMemberInfo(x.userid)['fullname']}\
                 for x in users]
        
    def supportsteams(self):
        proj, team=self.getProjectTeam()
        return proj is not None and team is None
        
    def getCurrentTeams(self):
        thelist=self.viewedlist()
        teams=thelist.teams.all()
        return teams
        
    def getAvailableTeams(self):
        teams=self.getCurrentTeams()
        
        project=self.context.getDBProject()
        #projectteams=utils.getTeamsInContext(project)
        result=DB.Team.objects.filter(project=project).exclude(id__in=[team.id for team in teams])
        return result

    def nonsubscribedMembers(self):
        all=self.AllMembers()
        table={}
        mtool = getToolByName(self.context, 'portal_membership')
        for userid in all:
            table[userid]=userid
        subscribed_ids=self.subscribedMembers()
        for userid in subscribed_ids:
            if userid['id'] in table:
                del table[userid['id']]
        users=sorted([k for k in table.iterkeys()],key=str.lower)
        return [{'id':x ,'name': mtool.getMemberInfo(x)['fullname']}\
                 for x in users] 

    def AllMembers(self):
        project=None
        team=None
        if hasattr(self.context,'getTeamUsers'):
            return self.context.getTeamUsers()
        if hasattr(self.context,'getProjectUsers'):
            return self.context.getProjectUsers()
        users=self.context.acl_users
        return users.getUserIds()


    def condition(self, *args, **kw):
        expanded=int(self.context.request.form['expanded'])
        if expanded>0:
            return False
        return True
        
    def getTarget(self, *args, **kw):
        listid=int(self.context.request.form['listid'])
        return 'table-%s'%listid
        
        
class HideMembers(KSSReplaceWrapper):

    def viewedlist(self):
        listid=int(self.context.request.form['listid'])
        dblist=DB.MailingList.objects.get(id=listid)
        return dblist

    def condition(self, *args, **kw):
        expanded=int(self.context.request.form['expanded'])
        if expanded>0:
            return True
        return False
        
    def getTarget(self, *args, **kw):
        listid=int(self.context.request.form['listid'])
        return 'table-%s'%listid
    
    def buildHtml(self):
        format="""
        <table class="listing" 
            id="table-%i" >
            <tr>
            <th colspan="2">
                %s
                <input type="button" value="+" class="mailinglistexpandable"/>
                
            </th>
        </tr>
        </table>
        """
        list=self.viewedlist()
        return format%(list.id,list.listname)
        
        
                