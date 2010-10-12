from Products.qi.cleanup import utils as clean
from Products.qi.util.general import BrowserPlusView

class Clean(BrowserPlusView):
    processFormButtons=("cleanteams","cleanprojects")
    
    def validate(self, form):
        pass
    
    def action(self, form, action):
        if action=="cleanteams":
            teams=self.getTeams()
            teams.delete()
        if action=="cleanprojects":
            projects=self.getProjects()
            projects.delete()
            
    def getTeams(self):
        site=self.context.qiteamspace
        return clean.findAbandonedDBTeams(site)
        
    def getProjects(self):
        site=self.context.qiteamspace
        return clean.findAbandonedDBProjects(site)