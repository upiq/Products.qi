from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import implements

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces import plugins as pluginifaces

from AccessControl import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass

class WhoPlugin(Folder, BasePlugin):
    """
    PAS multi-plugin for use with repoze.who
    """
    meta_type = "Who Plugin"

    manage_options = BasePlugin.manage_options + Folder.manage_options
    
    implements(pluginifaces.IAuthenticationPlugin,
               pluginifaces.IChallengePlugin,
               pluginifaces.IPropertiesPlugin,
               pluginifaces.ILoginPasswordExtractionPlugin,
               pluginifaces.ILoginPasswordHostExtractionPlugin,
               pluginifaces.ICredentialsUpdatePlugin,
               pluginifaces.ICredentialsResetPlugin)
    
    security = ClassSecurityInfo()

    def __init__(self, id):
        self._setId(id)

    # IAuthenticationPlugin interface

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """
        """
        userid = credentials.get('repoze.who.userid')
        if userid:
            username = credentials.get('login', userid)
            return userid, username
        
    # IChallengePlugin interface
    
    security.declarePublic('challenge')
    def challenge(self, request, response, **kw):
        """ Just raise unauthorized """
        from zExceptions import Unauthorized
        raise Unauthorized

    # IPropertiesPlugin interface
    
    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """
        Get user properties
        """
        if request is not None:
            return request.environ.get('repoze.who.identity')

    # IExtractionPlugin/ILoginPasswordExtractionPlugin/
    # ILoginPasswordHostExtractionPlugin interface

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        return request.environ.get('repoze.who.identity')

    # ICredentialsUpdate interface

    security.declarePublic('updateCredentials')
    def updateCredentials(self, request, response, login, new_password):
        """ Respond to change of credentials. """
        identity = request.environ.get('repoze.who.identity')
        if identity:
            identity['login'] = login
            identity['password'] = new_password
            return True

    # ICredentialsReset interface

    security.declarePublic('resetCredentials')
    def resetCredentials(self, request, response):
        """ Empty out the currently-stored session values """
        identity = request.environ.get('repoze.who.identity')
        if identity:
            identity['login'] = ''
            identity['password'] = ''
            return True


InitializeClass(WhoPlugin)

manage_addWhoPluginForm = PageTemplateFile(
    'www/addWhoPluginForm.pt', globals(),
    __name__='manage_addWhoPluginForm')

def manage_addWhoPlugin(container, id, REQUEST=None):
    """
    Add plugin to pluggable auth container
    """
    plugin = WhoPlugin(id)
    container._setObject(plugin.getId(), plugin)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'Who+Plugin+added.'
                                    % container.absolute_url() )
