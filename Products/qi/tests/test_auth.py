import unittest

class WhoPluginTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.qi.util.auth.whoplugin import WhoPlugin
        return WhoPlugin

    def _makeOne(self, id='test', *args, **kw):
        return self._getTargetClass()(id=id, *args, **kw)

    def test_authenticateCredentials(self):
        plugin = self._makeOne()
        creds = {'repoze.who.userid':'userid', 'login':'login'}
        result = plugin.authenticateCredentials(creds)
        self.assertEqual(result, ('userid', 'login'))

    def test_authenticateCredentials_nologin(self):
        plugin = self._makeOne()
        creds = {'repoze.who.userid':'userid'}
        result = plugin.authenticateCredentials(creds)
        self.assertEqual(result, ('userid', 'userid'))

    def test_authenticateCredentials_norepozewho(self):
        plugin = self._makeOne()
        creds = {}
        result = plugin.authenticateCredentials(creds)
        self.assertEqual(result, None)

    def test_challenge(self):
        plugin = self._makeOne()
        from zExceptions import Unauthorized
        self.assertRaises(Unauthorized, plugin.challenge, None, None)

    def test_getPropertiesForUser(self):
        plugin = self._makeOne()
        request = DummyRequest(environ={'repoze.who.identity':{'foo':'bar'}})
        result = plugin.getPropertiesForUser(None, request)
        self.assertEqual(result, {'foo':'bar'})

    def test_getPropertiesForUser_requestNone(self):
        plugin = self._makeOne()
        result = plugin.getPropertiesForUser(None, None)
        self.assertEqual(result, None)

    def test_updateCredentials(self):
        plugin = self._makeOne()
        identity = {'foo':'bar'}
        environ = {'repoze.who.identity':identity}
        request = DummyRequest(environ=environ)
        result = plugin.updateCredentials(request, None, 'newlogin',
                                          'newpassword')
        self.assertEqual(identity['login'], 'newlogin')
        self.assertEqual(identity['password'], 'newpassword')
        self.assertEqual(result, True)

    def test_updateCredentials_noidentity(self):
        plugin = self._makeOne()
        request = DummyRequest()
        result = plugin.updateCredentials(request, None, 'newlogin',
                                          'newpassword')
        self.assertEqual(result, None)

    def test_resetCredentials(self):
        plugin = self._makeOne()
        identity = {'foo':'bar'}
        environ = {'repoze.who.identity':identity}
        request = DummyRequest(environ=environ)
        result = plugin.resetCredentials(request, None)
        self.assertEqual(identity['login'], '')
        self.assertEqual(identity['password'], '')
        self.assertEqual(result, True)

    def test_resetCredentials_noidentity(self):
        plugin = self._makeOne()
        environ = {}
        request = DummyRequest(environ=environ)
        result = plugin.resetCredentials(request, None)
        self.assertEqual(result, None)

class TestManageAddWhoPlugin(unittest.TestCase):
    def _getFUT(self):
        from Products.qi.util.auth.whoplugin import manage_addWhoPlugin
        return manage_addWhoPlugin

    def test_it(self):
        request = DummyRequest()
        container = DummyContainer()
        f = self._getFUT()
        f(container, 'test', request)
        self.failUnless(request.RESPONSE.redirected.startswith(
            'http://example.com'))
        self.assertEqual(container.set[0], 'test')
        self.assertEqual(container.set[1].id, 'test')
        

class DummyContainer:
    set = None
    def _setObject(self, id, thing):
        self.set = (id, thing)

    def absolute_url(self):
        return 'http://example.com'
        
class DummyResponse:
    redirected = None
    def redirect(self, where):
        self.redirected = where

class DummyRequest:
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self.RESPONSE = DummyResponse()

    def __getitem__(self, name):
        return getattr(self, name)

def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])
