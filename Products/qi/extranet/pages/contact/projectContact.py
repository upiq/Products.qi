from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB

class ProjectContactForm(BrowserPlusView):
    processFormButtons=('update',)
    
    def validate(self, form):
        self.requiredEmail('email')
    
    
    def getCurrentEmail(self):
        if hasattr(self.context, 'ProjectEmail'):
            return self.context.ProjectEmail
        return ''
    
    def action(self, form, action):
        email=form['email']
        project=self.context.getProject()
        project.ProjectEmail=email
        
    def getProjectEmail(self):
        if hasattr(self.context, 'ProjectEmail'):
            return self.context.ProjectEmail
        else:
            possibleManagers=self.context.getProjectUsers('managers')
            if(len(possibleManagers)>0):
                return possibleManagers[0]
            else: 
                return None