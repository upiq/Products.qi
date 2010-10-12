from Products.qi.util.general import BrowserPlusView
class Success(BrowserPlusView):
    
    def home(self):
        return self.context.absolute_url()
    
    def target(self):
        raise Exception("attempt to use generic success page")