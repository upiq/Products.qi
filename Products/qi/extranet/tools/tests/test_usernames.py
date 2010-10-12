import unittest
class UsernameTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.qi.extranet.tools.QIRegistrationTool import QIRegistrationTool
        return QIRegistrationTool

    def _makeOne(self, id='test', *args, **kw):
        return self._getTargetClass()( *args, **kw)

    def getRegEx(self):
        regTool=self._makeOne()
        return regTool._ALLOWED_MEMBER_ID_PATTERN
    
    def test_Email(self):
        regEx=self.getRegEx()
        self.failUnless(regEx.match('good@example.com'))
        self.failUnless(regEx.match('GoOd@EXAMPLE.COM'))
        self.failUnless(regEx.match('Go.od@EXAMPLE.COM'))
        self.failUnless(regEx.match('Go.od@EXAMPLE.co.uk'))
        self.failUnless(regEx.match('Go_od@mail.example.com'))
        self.failUnless(regEx.match('Good@something-dashed.museum'))
        self.failUnless(regEx.match('user1234@welikenumbers.net'))

    def test_NonEmail(self):
        regEx=self.getRegEx()
        self.failIf(regEx.match('badexample'))
        self.failIf(regEx.match('badexample.com'))
        self.failIf(regEx.match('bad@example'))
        self.failIf(regEx.match('bad@example..com'))
        self.failIf(regEx.match('bad@@example.com'))
        self.failIf(regEx.match('very@bad@example.org'))
        self.failIf(regEx.match('example@bad.org.'))
        self.failIf(regEx.match('example@.org'))

def test_suite():
   return unittest.TestSuite((
        unittest.makeSuite(UsernameTests),))