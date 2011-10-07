from zope.component import createObject
from zope.formlib import form

from Acquisition import aq_inner, aq_self, aq_parent
from zExceptions import BadRequest
from Products.Five.browser import BrowserView
from string import upper
from Products.CMFCore.utils import getToolByName

from qi.sqladmin import models as DB
from DateTime import DateTime

from plone.app.form import base
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from Products.qi.extranet.users.qiuser import QiUsersSource as UsersSource
from plone.app.vocabularies.users import UsersSourceQueryView

from Products.qi.extranet.types.interfaces import IQITeam
from Products.qi.extranet.types.interfaces import IQISubTeam
from Products.qi.extranet.types.project import Project
from Products.qi.extranet.types.handlers.users import add_leads
from Products.qi import MessageFactory as _

from Products.qi.util.utils import getTeamsInContext
import os.path
import os
import time
import datetime


class TeamAddForm(base.AddForm):
    """Add form for teams
    """

    form_fields = form.Fields(IQITeam)

    label = _(u"Add Team")
    form_name = _(u"Team settings")

    def setUpWidgets(self, ignore_request=False):
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


class SubTeamAddForm(base.AddForm):
    """Add form for teams
    """

    form_fields = form.Fields(IQISubTeam)

    label = _(u"Add Team")
    form_name = _(u"Team settings")

    def setUpWidgets(self, ignore_request=False):
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

    form_fields = form.Fields(IQITeam) 

    label = _(u"Edit team")
    form_name = _(u"Team settings")
 
