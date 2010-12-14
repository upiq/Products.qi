
from zope.component import createObject
from zope.formlib import form

from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility

from Acquisition import aq_inner
from zExceptions import BadRequest
from Products.Five.browser import BrowserView
from Products.qi.util.general import BrowserPlusView
from Products.CMFCore.utils import getToolByName
from plone.portlets.manager import PortletManager
from DateTime import DateTime

from plone.app.form import base
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
#from plone.app.vocabularies.users import UsersSource
from Products.qi.extranet.users.qiuser import QiUsersSource as UsersSource
from plone.app.vocabularies.users import UsersSourceQueryView

from Products.qi.extranet.types.interfaces import IQIProject
from Products.qi import MessageFactory as _
from Products.qi.extranet.types.handlers.users import add_managers_and_faculty
from qi.sqladmin.models import Project as RelProject
from qi.sqladmin import models as DB
from datetime import datetime

from Products.qi.extranet.types.handlers import django as dbhandlers
from Products.qi.extranet.types import project as content
from Products.qi.util.utils import getTeamsInContext
from Products.CMFPlone.patches.unicodehacks import _unicode_replace
from Products.qi.util import utils


from Products.qi.util.utils import default_addable_types

project_form_fields = form.Fields(IQIProject)
#project_form_fields['managers'].custom_widget = UberMultiSelectionWidget
#project_form_fields['faculty'].custom_widget = UberMultiSelectionWidget

class ProjectAddForm(base.AddForm):
    """Add form for projects
    """

    form_fields = project_form_fields
    label = _(u"Add Project")
    form_name = _(u"Project settings")

    def setUpWidgets(self, ignore_request=False):
        """default_addable = default_addable_types(aq_inner(self.context))"""

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)

    def create(self, data):
        project = createObject(u"Products.qi.Project")
        form.applyChanges(project, self.form_fields, data)
        return project

class ProjectEditForm(base.EditForm):
    """Edit form for projects
    """

    form_fields = project_form_fields

    label = _(u"Edit Project")
    form_name = _(u"Project settings")
    
def compareMembers(member1,member2):
    return cmp(member1['name'].upper(),member2['name'].upper())

class ProjectMembersView(BrowserPlusView):

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

    def listProjectMembers(self):
        #mtool = getToolByName(self.context, 'portal_membership')
        group_id = self._getGroupId()
        plugin = self._getGroupsPlugin()
        ids = [x[0] for x in plugin.listAssignedPrincipals(group_id)]
        #names = [mtool.getMemberInfo(x)['fullname'] for x in ids]
        return self.getUserObjects(ids)
            #sorted([{'id': x[0],
            #     'name': x[1],
            #    } for x in zip(ids, names)], compareMembers)
                
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
        leads=[]
        teams=utils.getTeamsInContext(self.context)
        for team in teams:
            leads[len(leads):]=team.getTeamUsers('lead')
        
        return self.getUserObjects(leads)
        
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
        lact = dict(props).get('last_activity', '') # '' if property absent
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
 
    def update(self, *arge, **kw):
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
            except KeyError:
                #do nothing
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
                if 'notify' in form:
                    self.notifyUser(form['email'], password)
            except ValueError:
                self.errors="The email address is invalid or already in use."
                return
            
            form.clear()
        
        
        project=self.context.getProject()
        if 'users' in form:
            if 'Remove Member' in form:
                for user in form['users']:
                    self.removeManager(user)
                    self.removeFaculty(user)
                    self._removeUserFromGroup(user)
                form.clear()
                add_managers_and_faculty(project, None)
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
    
    def notifyUser(self, email, password):
        emailformat="""To: %s
From: noreply@qiteamspace.com
Subject: Registration for %s

You have been registered for a %s Account.
You have been assigned by your project manager the following login and password.
Both login and password are case sensitive.

Login: %s
Password: %s

visit %s to log in.
"""
        message=emailformat%(email,self.context.title,self.context.title,email, password,self.context.absolute_url())
        mailtool=getUtility(IMailHost)
        if email is not None:
            mailtool.send(message, email,'noreply@qiteamspace.com')
        

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

    def _getGroupId(self,groupname='members'):
        return self.context.getProjectGroup(groupname)

    def _getGroupsPlugin(self):
        acl_users = self.context.acl_users # acquire
        return acl_users.source_groups

    def _addUserToGroup(self, email, groupname='members'):
        group_id = self._getGroupId(groupname)
        plugin = self._getGroupsPlugin()
        plugin.addPrincipalToGroup(email, group_id)
        
    def _removeUserFromGroup(self, email, groupname='members'):
        group_id=self._getGroupId(groupname)
        plugin=self._getGroupsPlugin()
        teams=getTeamsInContext(self.context.getProject())
        if groupname=='members':
            for team in teams:
                teamgroup=team.getGroup()
                plugin.removePrincipalFromGroup(email, teamgroup)
        plugin.removePrincipalFromGroup(email, group_id)
        #lists=self.context.getDBProject().mailinglist_set.filter()
        if groupname=='members':
            lists=DB.MailingList.objects.filter(project=self.context.getDBProject())
            removed=DB.MailingListSubscriber.objects.filter(list__in=lists).filter(userid=email)
            removed.delete()
        
class Synchronize(BrowserView):
    def __call__(self, *args, **kw):
        project=self.context
        if not isinstance(project, content.Project):
            raise Exception
        dbhandlers.persistProjectToDjango(project, None)
        for child in project.getChildNodes():
            if isinstance(child, content.Team):
                dbhandlers.persistTeamToDjango(child,None)
        self.request.response.redirect(self.context.absolute_url())
    
    
    
