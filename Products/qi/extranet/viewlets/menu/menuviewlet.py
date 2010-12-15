from plone.app.layout.viewlets.common import ViewletBase
from menu import MenuItem
from zope.viewlet.interfaces import IViewletManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IMenu(IViewletManager):
    pass

class QIMenu(ViewletBase):
    #render = ViewPageTemplateFile('qi-menu.pt')
    
    def render(self, *args, **kw):
        return self.index(*args,**kw)
    
    def hasMenus(self):
        return True

    def contextHasMenus(self):
        return hasattr(self.context,"getMenuItems")
    
    baseItems=( 
        ("Measure_Type.html","Manage Measure Types","Role:Manager"),
        ("Add_Measure.html","Create New Measure","Role:Manager"),
        #("addreport.html","Create a Report","Role:Manager"),
        ("topics.html","Manage Topics","Role:Manager"))
    personalItems=(
        ("archives.html","View Mail Archives",'Role:Member'),
        ("newsend.html","Send Mail to My Mailing Lists",'Role:Member'),
        ("Subscribe.html","Subscribe to Mailing Lists",'Role:Member'))
    def getMenus(self):
        systemMenu=MenuItem(context=self.context, name="Shared Resources")
        systemMenu.items=[]
        if hasattr(self.context, 'getProject'):
            targetcontext=self.context.getProject()
        else:
            targetcontext=self.context
        for item in self.baseItems:
            systemMenu.items.append(MenuItem(context=targetcontext,
                target=item[0], name=item[1],permission=item[2]))
        personalMenu=MenuItem(context=self.context,name="Mail Options")
        personalMenu.items=[]
        for item in self.personalItems:
            personalMenu.items.append(MenuItem(context=self.context,
                target=item[0], name=item[1],permission=item[2]))
        contextmenus=[systemMenu,personalMenu]
        if self.contextHasMenus():
            contextmenus[2:]= self.context.getMenuItems()
        removed=[]
        for menu in contextmenus:
            anySubItems=False
            for option in menu.items:
                if option.hasPermission():
                    anySubItems=True
            if not anySubItems:
                removed.append(menu)
        for menu in removed:
            contextmenus.remove(menu)
        
        return contextmenus
    
    
