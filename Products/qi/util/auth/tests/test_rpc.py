import unittest
import Acquisition

class CheckCredentialsViewTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.qi.util.auth.rpc import CheckCredentialsView
        return CheckCredentialsView

    def _makeOne(self, context=None, request=None):
        if context is None:
            context = object()
        if request is None:
            request = {}
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IBrowserView(self):
        from zope.interface.verify import verifyClass
        from zope.publisher.interfaces.browser import IBrowserView
        verifyClass(IBrowserView, self._getTargetClass())

    def test_instance_conforms_to_IBrowserView(self):
        from zope.interface.verify import verifyObject
        from zope.publisher.interfaces.browser import IBrowserView
        verifyObject(IBrowserView, self._makeOne())

    def test_binarify(self):
        from Products.qi.util.auth.rpc import binarify
        result = binarify({'a':'1', 'b':'2', 'c':1})
        import xmlrpclib
        self.assertEqual(result['a'], xmlrpclib.Binary('1'))
        self.assertEqual(result['b'], xmlrpclib.Binary('2'))
        self.assertEqual(result['c'], 1)

    def test_debinarify(self):
        from Products.qi.util.auth.rpc import debinarify
        import xmlrpclib
        result = debinarify(
            {'a':xmlrpclib.Binary('1'),'b':xmlrpclib.Binary('2'),
             'c':1})
        self.assertEqual(result['a'], '1')
        self.assertEqual(result['b'], '2')
        self.assertEqual(result['c'], 1)

    def test_noauthenticators(self):
        pas = DummyPAS([])
        context = DummyContext()
        context.acl_users = pas
        view = self._makeOne(context)
        result = view({})
        self.assertEqual(result, {})

    def test_success(self):
        authenticator = DummySuccessAuthenticator()
        authenticators = [('authenticator', authenticator)]
        pas = DummyPAS(authenticators)
        context = DummyContext()
        context.acl_users = pas
        view = self._makeOne(context)
        identity = {'login':'foo', 'password':'bar'}
        result = view(identity)
        from Products.qi.util.auth.rpc import binarify
        self.assertEqual(result, binarify({'userid':'userid', 'login':'login'}))

    def test_fail(self):
        authenticator = DummyFailAuthenticator()
        authenticators = [('authenticator', authenticator)]
        pas = DummyPAS(authenticators)
        context = DummyContext()
        context.acl_users = pas
        view = self._makeOne(context)
        identity = {'login':'foo', 'password':'bar'}
        result = view(identity)
        self.assertEqual(result, {})

    def test_binaryinput(self):
        authenticator = DummySuccessAuthenticator()
        authenticators = [('authenticator', authenticator)]
        pas = DummyPAS(authenticators)
        context = DummyContext()
        context.acl_users = pas
        view = self._makeOne(context)
        import xmlrpclib
        identity = {'login':xmlrpclib.Binary('foo'),
                    'password':xmlrpclib.Binary('bar')}
        result = view(identity)
        from Products.qi.util.auth.rpc import binarify
        self.assertEqual(result, binarify({'userid':'userid', 'login':'login'}))

    def test_walkup(self):
        subfolder = DummyContext() # no acl_users
        portal = DummyContext()
        root = DummyContext()
        portal = portal.__of__(root)
        subfolder = subfolder.__of__(portal)
        failauthenticators = [('authenticator', DummyFailAuthenticator())]
        portal.acl_users = DummyPAS(failauthenticators)
        successauthenticators = [('authenticator', DummySuccessAuthenticator())]
        root.acl_users = DummyPAS(successauthenticators)
        view = self._makeOne(subfolder)
        import xmlrpclib
        identity = {'login':xmlrpclib.Binary('foo'),
                    'password':xmlrpclib.Binary('bar')}
        result = view(identity)
        from Products.qi.util.auth.rpc import binarify
        self.assertEqual(result, binarify({'userid':'userid', 'login':'login'}))

class DummyContext(Acquisition.Implicit):
    pass

class DummyUser:
    def __init__(self, id):
        self.id = id
        
    def getId(self):
        return self.id

class DummyUserFolder:
    def __init__(self, user):
        self.user = user

    def authenticate(self, login, password, request):
        # emulate root user folder
        return self.user

class DummyURLTool:
    def __init__(self, portal):
        self.portal = portal
        
    def getPortalObject(self):
        return self.portal

class DummySuccessAuthenticator:
    def authenticateCredentials(self, credentials):
        return 'userid', 'login'

class DummyFailAuthenticator:
    def authenticateCredentials(self, credentials):
        return None

class DummyPAS:
    def __init__(self, authenticators=()):
        self.authenticators = authenticators

    def _getOb(self, *arg):
        return self

    def listPlugins(self, *arg):
        return self.authenticators

def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])
