from Products.qi.util.general import BrowserPlusView

class RegisterType(BrowserPlusView):
    processFormButtons=('add','delete')
    def existingTypes(self):
        if hasattr(self.context, 'registeredtranslators'):
            return self.context.registeredtranslators
        return {}
    
    def validate(self, form):
        if 'add' in form:
            if self.required('name','Name'):
                if 'name' in self.existingTypes():
                    self.addError('name','A file type has that name already')
            self.required('classname','Class')
        if 'delete' in form:
            self.required('name')
            
    def action(self, form, action):
        if action=="add":
            existing=self.existingTypes()
            name=form['name']
            classname=form['classname']
            existing[name]=classname
            #set it just in case we started a new one! huzzah?
            self.context.registeredtranslators=existing
            
        if action=='delete':
            del self.context.registeredtranslators[form['name']]