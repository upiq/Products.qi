import unittest
class LoginTest(unittest.TestCase):
    
    def build(self):
        from Products.qi.extranet.tools.QIUsers import QIUsers
        return QIUsers()

    def test_login_nonuser(self):
        target=self.build()
        try:
            usera=target.getUserById('a@a.a')
            self.fail("fake user existed")
        except ValueError:
            # we passed this test
            pass
        try:
            usera=target.getUserById("A@A.A")
            self.fail("fake user existed(captial)")
        except ValueError:
            #passed this test too
            pass
        #call login code for A@A.A
        #call login code for a@a.a
        #verify both users don't exist
        
    def test_login_addeduser(self):
        target=self.build()
        
        target.add('a@a.a')
        
        #should this fail things are very bad
        a=target.getUserById('a@a.a')
        
        #this will fail until getuserbyid works correctly
        b=target=getUserById('A@A.A')
        
        self.assertEquals(a,b)
            
        pass
        #add user a@a.a
        #verify user a@a.a can login
        #verify user A@A.A can log in
        #call getuserbyid on a@a.a
        #call getuserbyid on A@A.A
        #verify users are the same
        
        


def test_suite():
   return unittest.TestSuite(())
        #unittest.makeSuite(LoginTest),))