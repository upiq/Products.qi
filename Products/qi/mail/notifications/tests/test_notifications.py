import unittest
from datetime import datetime, timedelta
class FakeBrain(object):
    def __init__(self, wrapped):
        self.wrapped=wrapped
    def getObject(self):
        return self.wrapped
class FakeMailer(object):
    mailed=None
    def __init__(self):
        self.mailed=[]
    def send(self, text, targets, sender):
        self.mailed.append((text,targets))
        
class FakeForum(object):
    posts=None
    title='Fake Forum'
    def absolute_url(self):
        return 'fakeurl://fake.fake'
    lastemail=None
    def __init__(self, posts, lastemail):
        self.posts=posts
        self.lastemail=lastemail
    def recentposts(self,sincedate):
        return self.posts

class FakePost(object):
    body=None
    def __init__(self, body):
        self.body=body

class FakeUser(object):
    def __init__(self, *args):
        self.permissions=args[:]
    def has_permission(self,permission, place):
        return permission in self.permissions

class FakeUserTool(object):
    users={'testa@testa':FakeUser('View'),
    'testb@testb':FakeUser()}
    def getUserById(self, userid):
        return self.users[userid]
    pass

class FakeContext(object):
    acl_users=FakeUserTool()
    
class FakeParent(object):

    pass
    

class Base(unittest.TestCase):
    def get_tested(self):
        from Products.qi.mail.notifications import main 
        fakecontext=FakeParent
        fakecontext.qiteamspace=FakeContext()
        return main.UpdateProcess(fakecontext,'qiteamspace')
class TestSendInfo(Base):
    def test_simple_case(self):
        tested=self.get_tested()
        tested.mailer=FakeMailer()#force a mock
        fakeforum=FakeForum((FakePost('hello world'),), datetime(2009,4,14))
        tested.context=FakeContext()
        fakeforum.subscribers=['testa@testa','notexistant']
        tested.sendinfo(FakeBrain(fakeforum))
        self.assertEquals(len(tested.mailer.mailed),1)
    def test_no_changes(self):
        tested=self.get_tested()
        tested.mailer=FakeMailer()#force a mock
        fakeforum=FakeForum((FakePost('hello world'),), datetime.today()+timedelta(1))
        tested.context=FakeContext()
        fakeforum.subscribers=['testa@testa','notexistant']
        tested.sendinfo(FakeBrain(fakeforum))
        #our mock doesn't conform to the behavior of actual forums, TODO: fix this
        self.assertEquals(len(tested.mailer.mailed),1)

def test_suite():
    return unittest.TestSuite((
         unittest.makeSuite(TestSendInfo),
         ))