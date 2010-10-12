import unittest

class TestAllUsersVocabulary(unittest.TestCase):
    def _getFUT(self):
        from Products.qi.extranet.types.vocabularies import all_users
        return all_users

    def test_it(self):
        outer = DummyContext()
        context = DummyContext()
        outer.context = context
        context.acl_users = DummyPAS()
        all_users = self._getFUT()
        vocab = all_users(outer)
        self.assertEqual(vocab.getTermByToken('userid1').value, 'login1')
        self.assertEqual(vocab.getTermByToken('userid2').value, 'login2')
        self.assertRaises(LookupError, vocab.getTermByToken,'userid3')
        
class DummyContext:
    pass

class DummyPAS:
    def searchUsers(self, **kw):
        return ( {'login':'login1', 'userid':'userid1',
                  'pluginid':'source_users'},
                 {'login':'login2', 'userid':'userid2',
                  'pluginid':'source_users'},
                 {'login':'login3', 'userid':'userid3',
                  'pluginid':'not_source_users'},
                 )
                  

def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])
