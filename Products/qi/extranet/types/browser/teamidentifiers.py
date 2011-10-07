from Products.Five.browser import BrowserView
from qi.sqladmin import models as DB

from datetime import datetime
from Products.qi.util.logger import logger
class Identifiers(BrowserView):
    errors={}
    def __call__(self, *args, **kw):
        self.request['disable_border']=True
        self.update(*args,**kw)
        return self.index(*args, **kw)
        
    def update(self, *args, **kw):
        form=self.request.form
        if 'add' in form:
            if self.validate(form):
                newname=form['name'].strip()
                form.clear()
                self.addidentifier(newname)
        if 'delimg.x' in form:
            delname=form['del'].strip()
            self.delidentifier(delname)
            
    
    def getIdentifiers(self):
        dbteam=self.context.getDBTeam()
        try:
            query=DB.TeamIdentifier.objects.filter(team=dbteam)
        except Exception, e:
            logger.handleException()
        return query
    
    def validate(self, form):
        self.errors={}
        foundErrors=False
        #basic form validation
        if 'name' not in form or form['name'].strip()=='':
            self.addError('name','Please enter a name')
            foundErrors=True
        if foundErrors:
            return False
        #database validation begins here
        nameWanted=form['name'].strip()
        dbteam=self.context.getDBTeam()
        otherteams=dbteam.project.team_set.all();
        try:
            teamidentifiers=DB.TeamIdentifier.objects.\
                filter(team__in=otherteams)
        except Exception, e:
            logger.handleException(e)

        taken=teamidentifiers.filter(value=nameWanted)
        if len(taken)>0:
            message='%s is in use by a team in this project'
            self.addError('name',message%nameWanted)
            return False
        return True
        
    def addidentifier(self, name):
    
        try:
            attachedID,existed=DB.Identifier.objects.get_or_create(
                identifier="QI teamspace nickname",
                idtype="Nickname")
        except Exception, e:
            logger.handleException(e)
        attachedID.save()
        
        team=self.context.getDBTeam()
        teamIdentifier=DB.TeamIdentifier()
        teamIdentifier.registrationdate=datetime.now()
        teamIdentifier.value=name
        teamIdentifier.team=team
        teamIdentifier.identifier=attachedID
        try:
            teamIdentifier.save()
        except Exception, e:
            logger.handleException(e)
            
    def delidentifier(self, name):
        teamid = DB.TeamIdentifier.objects.get(value=name, team=self.context.getDBTeam())
        teamid.delete()


    def addError(self, key, value):
        if self.errors.has_key(key):
            self.errors[key].append(value)
        else:
            self.errors[key]=[value,]
            
    def getError(self, key):
        if self.errors.has_key(key):
            #reduce the problem to a non-list
            #this particular page doesn't generate more than one error 
            #per field
            return self.errors[key][0]
        else:
            return None
    def url(self):
        return '%s/%s'%(self.context.absolute_url(),self.__name__)
