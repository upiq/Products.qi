from plone.app.layout.viewlets import common

class Maintenance(common.ViewletBase):
    def render(self, *args, **kw):
        return self.index(*args,**kw)
    
    def alternateContent(self):
        if hasattr(self.context,'NotificationBar'):
            return True
        return False
    def content(self):
        return self.context.NotificationBar.rawhtml