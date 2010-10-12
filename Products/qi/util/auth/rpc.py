from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.PluggableAuthService.interfaces.plugins import \
     IAuthenticationPlugin
import xmlrpclib
from Acquisition import aq_parent
from Acquisition import aq_inner

def binarify(d):
    new_d = {}
    for k, v in d.items():
        if isinstance(v, basestring):
            v = xmlrpclib.Binary(v)
        new_d[k] = v
    return new_d

def debinarify(d):
    new_d = {}
    for k, v in d.items():
        if isinstance(v, xmlrpclib.Binary):
            v = v.data
        new_d[k] = v
    return new_d

class CheckCredentialsView(BrowserView):
    """ Meant to be called via XML-RPC by repoze.who when it needs to
    authenticate credentials; it assumes it's checking against a PAS.

    Identity is spec'd in __call__ so mapply works; this won't work
    properly when called from a browser, only from an xmlrpc client.

    We walk up the tree consulting all PAS user folders for credentials.
    """
    def __call__(self, identity):
        context = self.context

        while context is not None:
            acl_users = getToolByName(context, 'acl_users', None)
            if acl_users is None:
                break

            plugins = acl_users._getOb('plugins', None)
            if plugins is None:
                break

            authenticators = plugins.listPlugins( IAuthenticationPlugin )
            identity = debinarify(identity)

            for authenticator_id, authenticator in authenticators:
                tup = authenticator.authenticateCredentials(identity)
                if tup is not None:
                    userid, login = tup
                    return binarify({'userid':userid, 'login':login})

            context = aq_parent(aq_inner(context))

        return {}

