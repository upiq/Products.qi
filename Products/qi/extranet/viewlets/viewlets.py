from Products.Five.browser import BrowserView
from zope.viewlet.interfaces import IViewlet
from zope.interface import implements
from plone.app.layout.viewlets import common
from Products.qi.extranet.types.project import Project
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
from zope.component import getMultiAdapter
from Products.CMFPlone.utils import safe_unicode
from cgi import escape

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

class PathViewlet(common.PathBarViewlet):
    render = ViewPageTemplateFile('QI.path_bar.pt')
    
    def domainStrip(self, url):
        return UtilitiesView(self.context, self.request).domainStrip(url)
 
    
class TitleViewlet(common.ViewletBase):

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.page_title = self.context_state.object_title
        self.portal_title = self.portal_state.portal_title

    def render(self):
        portal_title = safe_unicode(self.portal_title())
        page_title = safe_unicode(self.page_title())
        if page_title == portal_title:
            return u"<title>%s</title>" % (escape(portal_title))
        elif not hasattr(self.context, 'getProject'):
            return u"<title>%s &mdash; %s</title>" % (
                escape(safe_unicode(page_title)),
                escape(safe_unicode(portal_title)))
        elif not isinstance(self.context.aq_parent.aq_parent, Project):
            return u"<title>%s &mdash; %s</title>" % (
                escape(safe_unicode(page_title)),
                escape(safe_unicode(self.context.getProject().title)))
        else:
            return "<title>%s</title>"%(escape(self.context.getProject().title))
            
            
class UtilitiesView:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def domainStrip(self, url):
        # AC 2008-04-08 it aquires the domain name being used by the
        # project in order to determine if the second item on the breadcrumbs 
        # is needed
        urlChunks=url.split('/')
        domain=urlChunks[2]
        domain=domain.split(':')[0]
        return domain

