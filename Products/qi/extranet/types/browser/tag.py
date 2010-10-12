from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB

class TagTeams(BrowserPlusView):
    processFormButtons=('submit',)
    def action(self, form, aciton):
        for team in self.context.getDBProject.team_set.all():
            values=form.get('tags-%i'%team.id,())
            team.teamtag_set.all().delete()
            for value in values.split(' '):
                if value.trim():
                    added=DB.TeamTag()
                    added.tag=value
                    added.team=team
                    added.save()
    
    def existingtags(self):
        return DB.TeamTag.objects.filter(team__project=self.context.getDBProject()).select_related(1)
        