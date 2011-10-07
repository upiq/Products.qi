from zope.component import createObject
from zope.formlib import form

from Acquisition import aq_inner, aq_parent

from Acquisition import aq_inner
from zExceptions import BadRequest
from Products.Five.browser import BrowserView

from DateTime import DateTime
from Products.ATContentTypes.utils import DT2dt
from Products.CMFCore.utils import getToolByName

from plone.app.form import base
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from plone.app.vocabularies.users import UsersSource
from plone.app.vocabularies.users import UsersSourceQueryView

from Products.qi.extranet.types.handlers.users import add_managers_and_faculty, add_leads
from Products.qi.util.utils import project_containing, team_containing
from Products.qi.extranet.types.interfaces import IQITeam
from Products.qi import MessageFactory as _

from datetime import datetime
import time
#team_form_fields = form.Fields(IQITeam)

    
def compareMembers(a,b):
    return cmp(a['id'].lower(),b['id'].lower())


class TeamMembersView(BrowserView):

    errors = None
    users = None
    search_widget = None


    def _cache_tool(self, name):
        """get, cache in local state: tool by name"""
        attrname = '_%s' % name
        if not hasattr(self, attrname):
            setattr(self, attrname, getToolByName(self.context, name))
        return getattr(self, attrname)

    @property
    def reg_tool(self):
        return self._cache_tool('portal_registration')

    @property
    def mtool(self):
        return self._cache_tool('portal_membership')

    def getProjectTeam(self):
        return project_containing(self.context), team_containing(self.context)

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
        if hasattr(self.context,'getTeamUsers'):
            userids= self.context.getTeamUsers('lead')
            return self.getUserObjects(userids)
        else:
            return []

    def getUserObjects(self, ids):
         if len(ids)==0:
             return []
         mtool = self.mtool
         names=[mtool.getMemberInfo(x)['fullname'] for x in ids]
         logintimes=[mtool.getMemberById(x).getProperty('last_login_time') for x in ids]
         return sorted([
                         {'id':x[0],'name':x[1],'logintime':x[2]}
                         for x in zip(ids, names,logintimes)
             ], compareMembers)

    def isUserOnline(self, user):
        acl = self.context.acl_users
        user = acl.getUserById(user)
        user_prop_sheet = acl.mutable_properties.getPropertiesForUser(user)
        props = dict(user_prop_sheet.propertyItems())
        login_time = props.get('last_activity', props.get('login_time', None))
        if isinstance(login_time, DateTime):
            login_time = DT2dt(login_time)
            # get seconds since login via timedelta
            since_login = datetime.now(login_time.tzinfo) - login_time
            since_login = abs(since_login.seconds + since_login.days*86400)
            if since_login <= 900:
                return True
        return False


    def addNewUser(self, email, password, full_name):
        reg_tool = self.reg_tool
        reg_tool.addMember(email,
                           password,
                           properties={'fullname': full_name,
                                       'email': email,
                                       'username': email,
                                      })
        reg_tool.registeredNotify(email)
        self._addUserToGroup(email)

    def update(self, *args, **kw):
        mtool = self.mtool
        reg_tool = self.reg_tool
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
            if 'email' not in form or form['email']=='':
                self.errors = 'The email field was blank.'
                return 
            errorformat='The full name contained an invalid character.'
            for c in form['full_name']:
                if ord(c)>128:
                    self.errors=errorformat
                    return

            try:
                password = reg_tool.generatePassword()
                self.addNewUser(
                    form['email'],
                    password,
                    form['full_name'], )
            except ValueError:
                self.errors="The email address is invalid or already in use."
                return

            form.clear()

        project,team=self.getProjectTeam()
        if 'users' in form:
            if 'remove' in form:
                for user in form['users']:
                    self._removeUserFromGroup(user)
                form.clear()
            if 'Remove Member' in form:
                project,team=self.getProjectTeam()
                for user in form['users']:
                    self._removeUserFromGroup(user)
                    if team is not None:
                        self.removeLead(user)
                    else:
                        self.removeManager(user)
                        self.removeFaculty(user)
                if team is not None:
                    add_leads(team, None)
                else:
                    add_managers_and_faculty(project, None)
                form.clear()
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
            if 'Revoke Manager Status' in form:
                for user in form['users']:
                    self.removeManager(user)
                form.clear()
                add_managers_and_faculty(project, None)
            if 'Revoke Faculty Status' in form:
                for user in form['users']:
                    self.removeFaculty(user)
                form.clear()
                add_managers_and_faculty(project, None)
            if 'Grant Project Manager Status' in form:
                for user in form['users']:
                    self.removeFaculty(user)
                    self.addManager(user)
                form.clear()
                add_managers_and_faculty(project, None)
            if 'Make QIC' in form:
                for user in form['users']:
                    self.addQIC(user)
                form.clear()
            if 'Revoke QIC Status' in form:
                for user in form['users']:
                    self.removeQIC(user)
                form.clear()
            if 'Grant Faculty Status' in form:
                for user in form['users']:
                    self.removeManager(user)
                    self.addFaculty(user)
                form.clear()
                add_managers_and_faculty(project, None)

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
        
    def addManager(self, user):
        project=self.context.getProject()
        managers=project.managers
        if user not in managers:
            managers.append(user)
        project._p_changed=1;

    def removeManager(self, user):
        project=self.context.getProject()
        managers=project.managers
        if user in managers:
            managers.remove(user)
        project._p_changed=1;

    def addFaculty(self, user):
        project=self.context.getProject()
        faculty=project.faculty
        if user not in faculty:
            faculty.append(user)
        project._p_changed=1;
    def removeFaculty(self, user):
        project=self.context.getProject()
        faculty=project.faculty
        if user in faculty:
            faculty.remove(user)
        project._p_changed=1;
    def addQIC(self, user):
        self._addUserToGroup(user,'qics')
    def removeQIC(self, user):
        self._removeUserFromGroup(user,'qics')

    def url(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)

    def _getGroupId(self,groupname="members"):
        return self.context.getGroup(groupname)

    def _getProjectGroupId(self):
        
        return self.context.getProjectGroup()

    def _getGroupsPlugin(self):
        acl_users = self.context.acl_users # acquire
        return acl_users.source_groups

    def _addUserToGroup(self, email, groupname="members"):
        project, team=self.getProjectTeam()
        plugin = self._getGroupsPlugin()

        if team is not None:
            parent=aq_parent(aq_inner(self.context.getTeam()))
            try:
                parentteam=parent.getTeam()
                group_id=parentteam.getGroup()
                plugin.addPrincipalToGroup(email, group_id)            
            except AttributeError:
                pass

        group_id = self.context.getGroup(groupname)
        project_group_id=self._getProjectGroupId()
        plugin.addPrincipalToGroup(email, group_id)
        if project_group_id is not None and team is not None:
            plugin.addPrincipalToGroup(email, project_group_id)

    def _removeUserFromGroup(self, email, group="members"):
        group_id=self._getGroupId(group)
        plugin=self._getGroupsPlugin()
        plugin.removePrincipalFromGroup(email, group_id)
        project, team=self.getProjectTeam()

