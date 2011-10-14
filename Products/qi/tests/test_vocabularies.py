import unittest


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
