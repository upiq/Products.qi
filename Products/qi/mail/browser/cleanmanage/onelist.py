from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from Products.qi.util.utils import natsort, getUsersForMailingList
from Products.CMFCore.utils import getToolByName

from Products.qi.util.logger import actionlog

class ViewList(BrowserPlusView):
    processFormButtons=('addteams','removeteams','addmembers','removemembers','addgroups',\
        'removegroups','updatesettings')
    def first(self):
        self.dblist=DB.MailingList.objects.get(id=int(self.request.form['listid']))

    def generalUpdate(self):
        self.allusers=self.allUsers()
        self.curusers=self.currentUsers()
        self.availusers=self.availableUsers()
        self.processMembers()
        
        self.allgroups=self.allGroups()
        self.curgroups=self.currentGroups()
        self.availgroups=self.availableGroups()
        
        self.allteams=self.allTeams()
        self.curteams=self.currentTeams()
        self.availteams=self.availableTeams()
        
        self.reply=self.dblist.replyable
        self.subscribe=self.dblist.joinable
        self.description=self.dblist.description
        
        
    def allUsers(self):
        if hasattr(self.context,'getTeamUsers'):
            return self.context.getTeamUsers()
        if hasattr(self.context,'getProjectUsers'):
            return self.context.getProjectUsers()
        users=self.context.acl_users
        return users.getUserIds()
    def currentUsers(self):
        tool=getToolByName(self.context, 'acl_users')
        return natsort([x.userid for x in self.dblist.mailinglistsubscriber_set.all()],\
            lambda arg: tool.getUserById(arg).getProperty('fullname').lower())
    def availableUsers(self):
        tool=getToolByName(self.context, 'acl_users')
        return natsort([x for x in self.allusers if x not in self.curusers], \
            lambda arg: tool.getUserById(arg).getProperty('fullname').lower())
        
    def processMembers(self):
        tool=getToolByName(self.context, 'acl_users')
        self.allmembers=[tool.getUserById(x) for x in self.allusers]
        self.curmembers=[tool.getUserById(x) for x in self.curusers]
        self.availmembers=[tool.getUserById(x) for x in self.availusers]
    
    def allGroups(self):
        project, team=self.getDBProjectTeam()
        if team is not None:
            return ('members', 'leads')
        if project is not None:
            return ('members', 'faculty', 'contributers','leads','managers')
        return ()
    def currentGroups(self):
        return natsort([group.groupname for group in self.dblist.groups.all()])
    def availableGroups(self):
        return natsort([x for x in self.allgroups if x not in self.curgroups])
    
    def allTeams(self):
        project, team=self.getDBProjectTeam()
        if team is not None:
            return team.team_set.all()
        if project is not None:
            return project.team_set.all()
        return DB.Team.objects.none()
    def currentTeams(self):
        return natsort([t for t in self.dblist.teams.all()], lambda x: x.name.lower())
    def availableTeams(self):
        ids=[x.id for x in self.curteams]
        return natsort(self.allteams.exclude(id__in=ids), lambda x: x.name.lower())

    def validate(self, form):
        pass

    def action(self, form, action):
        if action=='addteams':
            self.addTeams(form)
        if action=='removeteams':
            self.removeTeams(form)
        if action=='addgroups':
            self.addGroups(form)
        if action=='removegroups':
            self.removeGroups(form)
        if action=='addmembers':
            self.addMembers(form)
        if action=='removemembers':
            self.removeMembers(form)
        if action=='updatesettings':
            self.updatesettings(form)
        
    def addTeams(self, form):
        if 'availteams' in form:
            teamids=form['availteams']
            if isinstance(teamids, (str, unicode)):
                added=DB.Team.objects.filter(id=teamids)
            else:
                added=DB.Team.objects.filter(id__in=teamids)
            print added
            for team in added:
                self.dblist.teams.add(team)
    def removeTeams(self, form):
        if 'curteams' in form:
            teamids=form['curteams']
            if isinstance(teamids, (str, unicode)):
                removed=DB.Team.objects.filter(id=teamids)
            else:
                removed=DB.Team.objects.filter(id__in=teamids)
            for team in removed:
                self.dblist.teams.remove(team)
                
    def addMembers(self, form):
        if 'availmembers' in form:
            userids=form['availmembers']
            actionlog.logText("users [%s] added to mailing list [%s] by %s"% \
                (userids,self.dblist.description,self.user()))
            if isinstance(userids,(str, unicode)):
                userids=[userids]
            for x in userids:
                added=DB.MailingListSubscriber()
                added.list=self.dblist
                added.userid=x
                added.save()
    def removeMembers(self, form):
        if 'curmembers' in form:
            userids=form['curmembers']
            actionlog.logText("users [%s] deleted from mailing list [%s] by %s"% \
                (userids,self.dblist.description, self.user()))
            if isinstance(userids,(str, unicode)):
                userids=[userids]
            subscribers=DB.MailingListSubscriber.objects.filter(list=self.dblist, userid__in=userids)
            subscribers.delete()
    
    def addGroups(self, form):
        if 'availgroups' in form:
            groups=form['availgroups']
            if isinstance(groups,(str, unicode)):
                groups=[groups]
            addedgroups=DB.SpecialMailGroup.objects.filter(groupname__in=groups)
            for addedgroup in addedgroups:
                self.dblist.groups.add(addedgroup)

    def removeGroups(self, form):
        if 'curgroups' in form:
            groups=form['curgroups']
            if isinstance(groups,(str, unicode)):
                groups=[groups]
            removedgroups=DB.SpecialMailGroup.objects.filter(groupname__in=groups)
            for removedgroup in removedgroups:
                self.dblist.groups.remove(removedgroup)
            
    def updatesettings(self, form):
        if 'description' in form:
            self.dblist.description=form['description']
        if 'allowsubscribe' in form:
            self.dblist.joinable=True
        else:
            self.dblist.joinable=False
        if 'allowreplies' in form:
            self.dblist.replyable=True
        else:
            self.dblist.replyable=False
        self.dblist.save()


class Overview(BrowserPlusView):
    def first(self):
        self.dblist=DB.MailingList.objects.get(id=int(self.request.form['listid']))
    def listname(self):
        return self.dblist.listname
    def members(self):
        tool=getToolByName(self.context, 'acl_users')
        ids=getUsersForMailingList(self.dblist, self.context)
        result= natsort([tool.getUserById(x) for x in ids], \
            lambda arg: arg.getProperty('fullname','').lower())
        return result
        