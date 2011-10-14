from Products.Five.browser import BrowserView
from zope.viewlet.interfaces import IViewlet
from zope.interface import implements
from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
from zope.component import getMultiAdapter


class LogoViewlet(BrowserView):

    implements(IViewlet)
    def __init__(self, context, request, view, manager):
        super(LogoViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        pass

    def render(self):
        securelogo = self.context.restrictedTraverse('logoprivate.jpg',None)
        logo = self.context.restrictedTraverse(_PROJECT_LOGO_NAME, None)
        if logo is None:
            logo=self.context.restrictedTraverse('logo.jpg', None)
        if securelogo is None:
            securelogo=logo
        portal_state = getMultiAdapter((self.context, self.request),
                                                    name=u'plone_portal_state')    
        #state=None
        """try:
            state = self.context.portal_workflow.getInfoFor(self.context, 'review_state')
        except:
            pass"""
        if not portal_state.anonymous():
            logo=securelogo
        hometag="<a class=\"logo\" href='%s'>%s</a>"
        if hasattr(self.context,'getProject'):
            homelink=self.context.getProject().absolute_url()
        else:
            homelink=self.context.absolute_url()
        return hometag%(homelink, logo.tag())

