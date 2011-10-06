from plone.app.layout.viewlets.common import ViewletBase
from menu import MenuItem
from zope.component import getMultiAdapter
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
        ("topics.html","Manage Topics","Role:Manager"))
    
    personalItems=()
    
    def _siteroot_link(self):
        portal_url = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state',).portal_url()
        return MenuItem(
            context=self.context,
            target=portal_url,
            name="Site root",
            permission="Role:Manager")
    
    def getMenus(self):
        systemMenu=MenuItem(context=self.context, name="Shared Resources")
        systemMenu.items=[]
        if hasattr(self.context, 'getProject'):
            targetcontext=self.context.getProject()
        else:
            targetcontext=self.context
        systemMenu.items.append(self._siteroot_link())
        for item in self.baseItems:
            systemMenu.items.append(MenuItem(context=targetcontext,
                target=item[0], name=item[1],permission=item[2]))
        contextmenus=[systemMenu,]
        if self.contextHasMenus():
            contextmenus[1:]= self.context.getMenuItems()
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
    
    
