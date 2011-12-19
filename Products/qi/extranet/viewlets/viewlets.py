from plone.app.layout.viewlets.common import LogoViewlet
from plone.app.layout.navigation.root import getNavigationRootObject

TAG = '<img src="%s" title="%s" alt="%s" />'


class ProjectLogoViewlet(LogoViewlet):
    
    def update(self):
        super(ProjectLogoViewlet, self).update()
        portal = self.portal_state.portal()
        navroot = getNavigationRootObject(self.context, portal)
        logo_title = navroot.Title()
        logofile = getattr(navroot, 'logo', None)
        if logofile is not None:
            filename = getattr(logofile, 'filename', None)
            if filename and logofile.getSize():
                # logo field has filename and data is not zero-byte/empty
                url = '%s/@@download/logo/%s' % (
                    self.navigation_root_url,
                    filename,
                    )
                self.logo_tag = TAG % (url, logo_title, logo_title)
        if 'project_logo.jpg' in navroot.contentIds():
            # backward-compatibility, old Products.qi custom logo content item
            url = '%s/project_logo.jpg/image' % self.navigation_root_url
            self.logo_tag = TAG % (url, logo_title, logo_title)

