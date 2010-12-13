from Products.Five.browser import BrowserView
#from Products.qi.datacapture.file import validationrules
#from Products.qi.datacapture.validation.rules import InvalidFunction
from qi.sqladmin import models as DB
from psycopg2 import IntegrityError 
import sys
import re
from datetime import date
from Products.qi.util.logger import logger
from Products.CMFCore.utils import getToolByName
from Products.qi.util.formvalidation import Validator
import AccessControl
__DEBUG__=True

class BrowserPlusView(BrowserView,Validator):
    
    #override to set buttons that cause an action
    processFormButtons=()
    #deprecated
    relatedPages=()
    #buttons that perform an action and skip validation(e.g. 'home')
    nonValidatedButtons=()
    #override or set to false to keep form data on success
    clearform=True
    removeBorders=True
    
    def __call__(self, *args, **kw):
        if self.removeBorders:
            self.request['disable_border']=self.removeBorders
        if __DEBUG__:
            self.update(*args, **kw)
            return self.index(*args, **kw)
        else:
            try:
                self.update(*args, **kw)
                return self.index(*args,**kw)
            except Exception, e:
                logger.handleException(e, self)
                self.doRedirect('Error.html')

    
    def update(self, *args, **kw):
        form=self.request.form
        self.first()
        for submission in self.processFormButtons:
            if submission in form:
                self.errors={}
                self.validate(form)
                if not self.hasErrors():
                    self.action(form, submission)
                    if self.clearform:
                        form.clear()
        for submission in self.nonValidatedButtons:
            if submission in form:
                self.action(form, submission)
        self.generalUpdate()

    def first(self):
        pass
    
    def action(self,form, action):
        raise NotImplementedError('action')
    
    def generalUpdate(self):
        #do non-form things here
        pass
    
    
    #convenience, back to start kind of thing
    def doRedirect(self, subUrl=''):
        redirectTarget='%s/%s'%(self.context.absolute_url(),subUrl)
        self.request.response.redirect(redirectTarget)
    
    def buildDate(self, string):
        if string.strip()=='':
            return None
        if string.find('/')>-1:
            items=string.split('/')
        else:
            items=string.split('-')
        month=int(items[0])
        day=int(items[1])
        year=int(items[2])
        return date(year,month,day)
        
    def generalTemplate(self):
        return context['general.pt'].macros['mainpage']
            
    def getRelatedPages(self):
        return self.relatedPages
    
    def validationSuportUrl(self):
        supportsite='http://ursa3.user.openhosting.com:8280/QITeamspaceSupport'
        subpage='help-center/how-to/validation/view'
        format='%s/%s'
        return format%(supportsite,subpage)
    
    def url(self):
        return '%s/%s'%(self.context.absolute_url(),self.__name__)
    
    def reformatdate(self, date):
        if date is not None:
            return "%i/%i/%i"%(date.month, date.day, date.year)
        else:
            return ""
        
    def niceifydt(self, datetimeo):
        if datetimeo is None:
            return ""
        ourformat='%s, %s:%s:%s'%(datetimeo.date(),
            self.clean(datetimeo.hour), 
            self.clean(datetimeo.minute),
            self.clean(datetimeo.second))
        return ourformat
    
    def clean(self, something):
        if something<10:
            return "0%i"%something
        return "%i"%something
    
    def getDBProjectTeam(self):
        dbproject=None
        dbteam=None
        if hasattr(self.context, 'getDBProject'):
            dbproject=self.context.getDBProject()
        if hasattr(self.context, 'getDBTeam'):
            dbteam=self.context.getDBTeam()
            
        return dbproject, dbteam
        
    def sortlist(self,lists, comparefunc):
        if len(lists)==1 or len(lists)==0:
            return lists
        midpoint=len(lists)/2
        leftsorted=self.sortlist(lists[:midpoint],comparefunc)
        rightsorted=self.sortlist(lists[midpoint:],comparefunc)
        result=[]
        while len(leftsorted)+len(rightsorted)>0:
            if len(leftsorted)==0:
                result.append(rightsorted.pop(0))
            elif len(rightsorted)==0:
                result.append(leftsorted.pop(0))
            elif comparefunc(leftsorted[0], rightsorted[0])>0:
                result.append(rightsorted.pop(0))
            else:
                result.append(leftsorted.pop(0))
        
        return result
        
    def getProjectTeam(self):
        project=None
        team=None
        if hasattr(self.context, 'getProject'):
            project=self.context.getProject()
        if hasattr(self.context, 'getTeam'):
            team=self.context.getTeam()
            
        return project, team
    
            
    def user(self):
        sec=AccessControl.getSecurityManager()
        user=sec.getUser()
        return str(user.getId())
    
    def email(self):
        uid=self.user()
        mtool=getToolByName(self.context,'portal_membership')
        member=mtool.getMemberById(uid)
        return member.getProperty('email','')
