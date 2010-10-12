
from Products.qi.util.general import BrowserPlusView

class AlterType(BrowserPlusView):
    processFormButtons=('change' ,)
    def currentType(self):
        return self.context.portal_type
    
    def validate(self, form):
        self.required('typename')
    
    def action(self,form,action):
        self.context.portal_type=form['typename']
        self.doRedirect("view")