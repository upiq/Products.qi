from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB

class TeamManagement(BrowserPlusView):
    processFormButtons=('update.x',)
    
    def validate(self, form):
        self.requiredInForm('start')
        self.requiredInForm('end')
        self.requiredInForm('id')
        self.requiredInForm('qic')
        self.requiredInForm('active')
        try:
            checked=zip(form['id'],form['start'],form['end'],form['qic'])[1:]
            for teamid, start,end,qic in checked:
                try:
                    self.buildDate(start)
                except:
                    self.addError('start','the starting date %s was incorrectly formatted'%start)
                try:
                    self.buildDate(end)
                except:
                    self.addError('end','the ending date %s was incorrectly formatted'%end)
        except:
            self.addError('id','The form submitted was incorrectly formatted.')
        #self.requiredInTable(self.teams(),'id')
        #self.optionalDate('start')
        #self.optionalDate('end')
    
    def action(self, form, action):
        changed=zip(form['id'],form['start'],form['end'],form['qic'])[1:]
        print form
        for teamid,startdate,enddate,qic in changed:
            team=self.teams().get(id=int(teamid))
            team.startdate=self.buildDate(startdate)
            team.enddate=self.buildDate(enddate)
            active=form.get('active-%i'%team.id,None)
            team.active=(active is not None)
            if qic!=None and qic!='':
                team.qic=qic
            team.save()              
    
    def teams(self):
        dbproj=self.context.getDBProject()
        return DB.Team.objects.filter(project=dbproj).order_by('name')
    
    def qics(self):
        return self.context.getProjectUsers('qics')