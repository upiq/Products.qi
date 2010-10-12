from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB

class ProjectReassociateForm(BrowserPlusView):
    processFormButtons=('change',)
    
    def validate(self, form):
        self.requiredInTable(DB.Project.objects,'dbid')
    
    def action(self, form, action):
        self.context.dbid=int(form['dbid'])
    
    def getProjects(self):
        return DB.Project.objects.all()


class TeamReassociateForm(BrowserPlusView):
    processFormButtons=('change',)
    
    def validate(self, form):
        self.requiredInTable(DB.Team.objects,'dbid')
    
    def action(self, form, action):
        self.context.dbid=int(form['dbid'])
    
    def getTeams(self):
        return DB.Team.objects.all()
    