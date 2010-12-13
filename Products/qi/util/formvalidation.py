from Products.Five.browser import BrowserView
from Products.qi.datacapture.validation import validationrules
from Products.qi.datacapture.validation.rules import InvalidFunction
from qi.sqladmin import models as DB
from psycopg2 import IntegrityError 
import sys
import re
from datetime import date
from Products.qi.util.logger import logger
from Products.CMFCore.utils import getToolByName
import AccessControl
from Globals import InitializeClass


from AccessControl import ClassSecurityInfo

class ErrorHolder:
    #used to store errors accumulated
    errors={}
    security=ClassSecurityInfo()
    
    def validate(self,form):
        self.addError('base','Validation not implemented')
        return False
        
    def addError(self, key, value):
      if self.errors.has_key(key):
          self.errors[key].append(value)
      else:
          self.errors[key]=[value,]

    def hasErrors(self):
      return len(self.errors)>0
      
      
    security.declarePublic('getError')
    def getError(self, key):
      if self.errors.has_key(key):
          return self.errors[key]
      else:
          return None
          
    def getErrors(self):
        result=[]
        for x in self.errors.itervalues():
            result+=x
        return result

InitializeClass(ErrorHolder)
      
class Validator(ErrorHolder):
    
    def requiredLength(self, key, length,longname=None):
        if longname is None:
            longname=key
        if not self.required(key, longname):
            return False
        form=self.request.form
        value=form[key]
        if len(value)<length:
            self.addError(key,'%s must be %i characters or longer'%(longname,length))
        return True
    
    def required(self, key, longname=None):
        if longname is None:
            longname=key
        form=self.request.form
        if not self.requiredInForm(key):
            return False
        if form[key]=='':
            self.addError(key,'%s is a required field.'%longname)
            return False
        return True
    
    def optionalDate(self, key, longname=None):
        if longname is None:
            longname=key
        form=self.request.form
        if not self.requiredInForm(key,longname):
            return False
        if form[key].strip() != '':
            return self.requiredDate(key,longname)
        return True

    
    def requiredDate(self, key, longname=None):
        if longname is None:
            longname=key
        form=self.request.form
        if not self.required(key,longname):
            return False
        string=form[key]

        items=string.split('/')
        if len(items)!=3:
            #return self.requiredDashDate(key, longname)
            self.addError(key, '%s is not MM/DD/YYYY'%longname)
            return False
        try:
            month=int(items[0])
            day=int(items[1])
            year=int(items[2])
            if year<1900:
                self.addError(key,"%s is before 1900"%longname)
            test=date(year,month,day)
        except ValueError:
            self.addError(key,'%s is not MM/DD/YYYY'%longname)
            return False
        except OverflowError:
            self.addError(key,'%s is out of range'%longname)
            return False
            
        return True
    
        
    def requiredInForm(self, key, longname=None):
        if longname is None:
            longname=key
        form=self.request.form
        if key not in form:
            self.addError(key,'%s is missing'%longname)
            self.addError('base','%s was missing in the form'%longname)
            return False
        return True
    
    def requiredInTable(self, query, key,longname=None,nullable=False):
        if longname is None:
            longname=key
        form=self.request.form
        if not self.required(key,longname):
            return False
        value=form[key]
        try:   
            idval=int(value)
        except ValueError:
            self.addError(key,'%s is an invalid value'%longname)
            return False
        if idval<0:
            if not nullable:
                self.addError(key,'Please select a value for %s'%longname)
                return False
            else:
                return True
        result=query.filter(id=idval)
        if len(result)<1:
            self.addError('base',
                '%s could not be found in the system'%longname)
            return False
        return True
    
    def requiredAvailable(self, query, key, column=None, longname=None):
        if longname is None:
            longname=key
        if column is None:
            column=key
        form=self.request.form
        if not self.required(key,longname):
            #no further validation possible
            return False
        value=form[key]
        format='LOWER(%s)='%column+'%s'
        #the second %s is filled by extra params
        queryset=query.extra(where=[format],params=[value.lower()])
        if len(queryset)>0:
            message='%s is already taken as a %s'%(value, longname)
            self.addError(key,message)
            return False
        return True
    
    def requiredValidation(self, key, longname=None):
        if longname==None:
            longname=key
        form=self.request.form
        if not self.requiredInForm(key,longname):
            return False
        value=form[key]
        try:
            rule=validationrules.buildRule(value)
        except validationrules.InvalidExpression, e:
            format='Invalid validation expression syntax: "%s" in %s'
            message=format%(e.text,longname)
            self.addError(key,message)
            return False
        except InvalidFunction, e:
            format='Unknown validation rule: %s in %s'
            message=format%(e.text,longname)
            self.addError(key, message)
            return False
        if not rule:
            format='% validation compile failed for unknown reason'
            message=format%longname
            self.addError(key,message)
            return False
        return True
    
    def requiredInt(self,key, longname=None):
        form=self.request.form
        if longname is None:
            longname=key
        if not self.required(key, longname):
            return False
        trimmed=form[key].strip()
        try:
            int(trimmed)
        except ValueError:
            self.addError(key,"%s is not a number"%longname)
            return False
        return True
    
    def requiredVersionNumber(self, key, longname=None):
        if longname is None:
            longname=key
        form = self.request.form
        if not self.required(key, longname):
            return False
        versionparts=form[key].split('.')
        try:
            for part in versionparts:
                int(part)
        except ValueError:
            format='%s is not a version number.'
            self.addError(key,format%longname)
            return False
        return True
    
    def present(self,key):
        form=self.request.form
        return key in form and form[key].strip()!=""
        
    def requiredEmail(self, key, longname=None):
        if longname is None:
            longname=key
        form=self.request.form
        if not self.required(key, longname):
            return False
        expression='^[A-Za-z][A-Za-z0-9_.]*@[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)+$'
        test=re.compile(expression)
        value=form[key]
        if not test.match(value):
            format='%s is not a valid email'
            self.addError(key, format%value)
            return False
        return True
    def daterange(self,startkey, endkey,startoptional=False,endoptional=False):
        form=self.request.form
        if not startoptional:
            if not self.requiredDate(startkey,'Start Date'):
                return False
        else:
            if not self.optionalDate(startkey,'Start Date'):
                return False
        if not endoptional:
            if not self.requiredDate(endkey,'End Date'):
                return False
        else:
            if not self.optionalDate(endkey,'End Date'):
                return False
        if self.present(startkey) and self.present(endkey):
            start=self.buildDate(form[startkey])
            end=self.buildDate(form[endkey])
            if start>end:
                self.addError(startkey,"Start date must come before end date")
                self.addError(endkey,"End date must come after start date")
                return False
        return True