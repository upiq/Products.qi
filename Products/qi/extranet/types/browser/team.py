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
