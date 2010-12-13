from zope.component import createObject
from zope.formlib import form

from Acquisition import aq_inner, aq_self, aq_parent
from zExceptions import BadRequest
from Products.Five.browser import BrowserView
from Products.qi.util.general import BrowserPlusView
from string import upper
from Products.CMFCore.utils import getToolByName

from qi.sqladmin import models as DB
from DateTime import DateTime

from plone.app.form import base
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from Products.qi.extranet.users.qiuser import QiUsersSource as UsersSource
#from plone.app.vocabularies.users import UsersSource
from plone.app.vocabularies.users import UsersSourceQueryView

from Products.qi.extranet.types.interfaces import IQITeam
from Products.qi.extranet.types.interfaces import IQISubTeam
from Products.qi.extranet.types.project import Project
from Products.qi.extranet.types.handlers.users import add_leads
from Products.qi import MessageFactory as _

from Products.qi.util.utils import default_addable_types, getTeamsInContext
import os.path
import os
import time
import datetime

team_form_fields = form.Fields(IQITeam)
#team_form_fields['managers'].custom_widget = UberMultiSelectionWidget

class TeamAddForm(base.AddForm):
    """Add form for teams
    """

    form_fields = team_form_fields

    label = _(u"Add Team")
    form_name = _(u"Team settings")

    def setUpWidgets(self, ignore_request=False):
        default_addable = default_addable_types(aq_inner(self.context))

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)

    def create(self, data):
        team = createObject(u"Products.qi.Team")
        form.applyChanges(team, self.form_fields, data)
        return team
        
    def failure_handler(self,form, action, data, error):
        self.status=error
        
    def validate(self,action, data):
        if (self.teamAlreadyExists()):
            print 'already exists'
            action.failure_handler=self.failure_handler
            return "A team with that name already exists in the project."
        return super(TeamAddForm,self).validate(action,data)
            
    def teamAlreadyExists(self):
        form=self.request.form
        if 'form.title' in form:
            teamname=form['form.title']
            project=self.context.getProject()
            teams=getTeamsInContext(project)
            for team in teams:
                if upper(team.title)==upper(teamname):
                    return True
        return False

team_form_fields = form.Fields(IQISubTeam)

class SubTeamAddForm(base.AddForm):
    """Add form for teams
    """

    form_fields = team_form_fields

    label = _(u"Add Team")
    form_name = _(u"Team settings")

    def setUpWidgets(self, ignore_request=False):
        default_addable = default_addable_types(aq_inner(self.context))

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)

    def create(self, data):
        team = createObject(u"Products.qi.SubTeam")
        form.applyChanges(team, self.form_fields, data)
        return team

    def failure_handler(self,form, action, data, error):
        self.status=error

    def validate(self,action, data):
        if (self.teamAlreadyExists()):
            print 'already exists'
            action.failure_handler=self.failure_handler
            return "A team with that name already exists in the project."
        return super(SubTeamAddForm,self).validate(action,data)

    def teamAlreadyExists(self):
        form=self.request.form
        if 'form.title' in form:
            teamname=form['form.title']
            project=self.context.getProject()
            teams=getTeamsInContext(project)
            for team in teams:
                if upper(team.title)==upper(teamname):
                    return True
        return False


class TeamEditForm(base.EditForm):
    """Edit form for team
    """

    form_fields = team_form_fields

    label = _(u"Edit team")
    form_name = _(u"Team settings")
    
def compareMembers(member1,member2):
    return cmp(member1['name'].upper(),member2['name'].upper())


class TeamMembersView(BrowserPlusView):

    errors = None
    users = None
    search_widget = None

    def getSearchWidget(self):
        if self.users is None:
            self.users = UsersSource(self.context)
        if self.search_widget is None:
            self.search_widget = UsersSourceQueryView(self.users, self.request)
        return self.search_widget

    def __call__(self, *args, **kw):
        self.request['disable_border']=True
        self.update(*args, **kw)
        return self.index(self, *args, **kw)

    #leaving this method name as project so we can reuse the 
    #template from project additions.
    #it might technically be possible to simply reuse the class for that as well
    def listProjectMembers(self):
        group_id = self._getGroupId()
        plugin = self._getGroupsPlugin()
        ids = [x[0] for x in plugin.listAssignedPrincipals(group_id)]
        return self.getUserObjects(ids)
                
    def listManagers(self):
        userids= self.context.getProjectUsers('managers')
        return self.getUserObjects(userids)
    
    def listFaculty(self):
        userids=self.context.getProjectUsers('faculty')
        return self.getUserObjects(userids)
    
    def listQics(self):
        userids=self.context.getProjectUsers('qics')
        return self.getUserObjects(userids)
        
    def listLeads(self):
        userids= self.context.getTeamUsers('lead')
        return self.getUserObjects(userids)
    
    def getUserObjects(self, ids):
         if len(ids)==0:
             return []
         mtool= getToolByName(self.context,'portal_membership')
         names=[mtool.getMemberInfo(x)['fullname'] for x in ids]
         logintimes=[mtool.getMemberById(x).getProperty('last_login_time') for x in ids]
         return sorted([
                         {'id':x[0],'name':x[1],'logintime':x[2]}
                         for x in zip(ids, names,logintimes)
             ], compareMembers)
             
    def isUserOnline(self, user):
        time = DateTime()
        acl = self.context.acl_users
        user = acl.getUserById(user)
        props = acl.mutable_properties.getPropertiesForUser(user).propertyItems() #gets user property sheet
        lact = dict([(m[0],m[1]) for m in props])['last_activity'] #turn list of tuples into dict
                                                                    #to get user's last activity
        if lact is not '':
            curtime = DateTime(lact)
            if(time - curtime <= .01): #any activity within the last 15 mins?
                return True

        return False
        

    def addNewUser(self, email, password, full_name):
        reg_tool = getToolByName(self.context, 'portal_registration')
        reg_tool.addMember(email,
                           password,
                           properties={'fullname': full_name,
                                       'email': email,
                                       'username': email,
                                      })
        self._addUserToGroup(email)
 
    def update(self, *args, **kw):
        mtool = getToolByName(self.context, 'portal_membership')
        form = self.request.form

        self.found = self.getSearchWidget().results('users') or ()

        self.found = [{'username': x,
                       'fullname': mtool.getMemberInfo(x)['fullname'],
                      } for x in self.found]

        if 'add_selected_users' in form:
            
            try:
                for userid in form['selected']:
                    self._addUserToGroup(userid)
            except KeyError , e:
                #do nothing
                #they did not select anyone
                pass

            form.clear()

        if 'add_new_user' in form:
            password, confirm = form['password'], form['confirm']


            if 'email' not in form or form['email']=='':
                self.errors = 'The email field was blank.'
                return 
            if password != confirm:
                self.errors = 'The password and confirmation do not match.'
                return
                
            if len(password)<5:
                self.errors= 'The password is shorter than 5 characters.'
                return
            errorformat='The full name contained an invalid character.'
            for c in form['full_name']:
                if ord(c)>128:
                    self.errors=errorformat
                    return

            try:
                self.addNewUser(form['email'],
                            password,
                            form['full_name'],
                           )
            except ValueError:
                self.errors="The email address is invalid or already in use."
                return
            
            form.clear()

        team=self.context.getTeam()
        if 'users' in form:
            if 'remove' in form:
                for user in form['users']:
                    self._removeUserFromGroup(user)
                form.clear()
            if 'Remove Member' in form:
                for user in form['users']:
                    self.removeLead(user)
                    self._removeUserFromGroup(user)
                form.clear()
                add_leads(team, None)
            if 'Revoke Team Lead Status' in form:
                for user in form['users']:
                    self.removeLead(user)
                form.clear()
                add_leads(team, None)
            if 'Grant Team Lead Status' in form:
                for user in form['users']:
                    self.addLead(user)
                form.clear()
                add_leads(team, None)
            
    def addLead(self, user):
        team=self.context.getTeam()
        managers=team.managers
        if user not in managers:
            managers.append(user)
        team._p_changed=1;

    def removeLead(self, user):
        team=self.context.getTeam()
        managers=team.managers
        if user in managers:
            managers.remove(user)
        team._p_changed=1;

    def url(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)

    def _getGroupId(self):
        return self.context.getGroup()

    def _getProjectGroupId(self):
        return self.context.getProjectGroup()

    def _getGroupsPlugin(self):
        acl_users = self.context.acl_users # acquire
        return acl_users.source_groups

    def _addUserToGroup(self, email):
        parent=aq_parent(aq_inner(self.context.getTeam()))
        plugin = self._getGroupsPlugin()
        try:
            parentteam=parent.getTeam()
            group_id=parentteam.getGroup()
            plugin.addPrincipalToGroup(email, group_id)            
        except AttributeError:
            pass

        group_id = self._getGroupId()
        project_group_id=self._getProjectGroupId()
        plugin.addPrincipalToGroup(email, group_id)
        if project_group_id is not None:
            plugin.addPrincipalToGroup(email, project_group_id)
    
    def _removeUserFromGroup(self, email):
        group_id=self._getGroupId()
        plugin=self._getGroupsPlugin()
        plugin.removePrincipalFromGroup(email, group_id)
        lists=self.context.getDBTeam().mailinglist_set.all()
        removed=DB.MailingListSubscriber.objects.filter(userid=email).filter(list__in=lists)
        #next delete those
        print 'as user is removed from team: deleting %s from %s'%(email,removed)
        removed.delete()



class AvailableReportsView(BrowserView):

    def __call__(self, *args, **kw):
        if self.update(*args, **kw):
            return self.index(self, *args, **kw)
        
    def update(self, *arge, **kw):
        if 'target' in self.request:
            if not self.validate(self.request):
                return True
            #security goes here
            target=self.request['target']
            #turn the file into bytes
            pdf=open(target).read()
            
            pieces=target.split('/')
            name=pieces[len(pieces)-1]
            
            RESPONSE=self.request.response
            RESPONSE.setHeader("Content-Length",len(pdf))
            RESPONSE.setHeader('Content-Type', 'application/pdf')
            RESPONSE.setHeader('Content-disposition','inline; filename="%s"' % (name))
            RESPONSE.write(pdf)
            return False
        return True
        
    def validate(self,request):
        try:
            target=request['target']
            if not target:
                return False
        except KeyError:
            #this exception should never happen
            return False
        
        if not os.path.isfile(target):
            return false
            
        #now verify that the team is our own
        #this prevents teams from manually triggering a 
        #pdf belonging to another team
        foundFolder=False
        allowedFolders=self.context.reportLocations
        if not allowedFolders:
            return False
        for folder in allowedFolders:
            if target.startswith(folder):
                foundFolder=True
        if not foundFolder:
            return False
        
        #if it doesn't fail anything above it's good
        return True    
                    
    def reportfolders(self):
        if not self.context.reportLocations:
            return ()
        else:
            result=[]
            removed=[]
            for k in self.context.reportLocations.iterkeys():
                if os.path.isdir(k):
                    folder=FolderListing()
                    folder.path=k
                    result.append(folder)
                else:
                    removed.append(k)
            for i in removed:
                del self.context.reportLocations[i]
        return result
    
    def encodeTarget(self,folder, filename):
        formula='%s/%s?target=%s/%s'
        members=(self.context.absolute_url(),self.__name__,folder.path,filename)
        return formula%members
        

class FolderListing:
    path=''
    
    def reportName(self):
        pathparts=self.path.split('/')
        last=pathparts[len(pathparts)-1]
        return last
    
    def items(self):
        #open the folder
        files=os.listdir(self.path)
        result=[]
        for f in files:
            if f.lower().endswith('.pdf'):
                result.append(f)
        return result
        
    def timestamp(self, item):
        itempath=self.path+'/'+item
        stats=os.stat(itempath)
        return datetime.datetime.fromtimestamp(stats.st_mtime)