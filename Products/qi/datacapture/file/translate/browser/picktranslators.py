from Products.qi.util.general import BrowserPlusView

class Pick(BrowserPlusView):
    
    processFormButtons=("add","remove")
    
    def allTypes(self):
        if hasattr(self.context, 'registeredtranslators'):
            return [k for k in self.context.registeredtranslators.iterkeys()]
        return []
    
    def usedTypes(self, cleanonteam=True):
        project, team=self.getProjectTeam()
        result={}
        if project is not None:
            if hasattr(project, 'translators'):
                for translator in project.translators:
                    result[translator]=translator
        if team is not None:
            if cleanonteam:
                result={}
            if hasattr(team, 'translators'):
                for translator in team.translators:
                    result[translator]=translator
        return [k for k in result.iterkeys()]
    
    def unusedTypes(self):
        taken={}
        for k in self.usedTypes(False):
            taken[k]=None
        return [k for k in self.allTypes() if k not in taken]
        
    def validate(self, form):
        if "add" in form:
            if self.requiredInForm("added"):
                if form['added']=='-1':
                    self.addError('added','Please choose a value to add')
            
        if "remove" in form:
            if self.requiredInForm("removed"):
                if form['removed']=='-1':
                    self.addError('removed','Please choose a value to remove')

    def action(self, form, action):
        project, team=self.getProjectTeam()
        target=team
        used=self.usedTypes()
        if target is None:
            target=project
        if action=="add":
            used.append(form['added'])
        if action=="remove":
            used.remove(form['removed'])
        self.context.translators=used