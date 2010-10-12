import unittest
from datetime import datetime

class FakeSet:
    def get(self,*args, **kw):
        return self.getval

class FakeForm:
    objects=FakeSet()
class FakeTeam:
    objects=FakeSet()

class FakeContext:
    objects=FakeSet()
    def getDBTeam(self):
        return self.dbteamobj
    

class FakeRequest:
    pass

class WindowTest(unittest.TestCase):
    formset=None
    teamset=None
    def setUp(self):
        from Products.qi.datacapture.form.entry import entry
        self.formset=FakeSet()
        self.teamset=FakeSet()
        self.teamobj=FakeTeam()
        self.teamobj.startdate=None
        self.teamobj.enddate=None
        FakeForm.objects=self.formset
        FakeTeam.objects=self.teamset
        self.faked=FakeForm()
        self.faked.daysforwardwindow=None
        self.faked.daysbackwardwindow=None
        self.formset.getval=self.faked
        entry.DB.Form=FakeForm
        entry.DB.Team=FakeTeam

    
    def build(self):
        from Products.qi.datacapture.form.entry import entry
        self.request=FakeRequest()
        self.request.form={}
        self.context=FakeContext()
        self.context.request=self.request
        self.context.dbteamobj=self.teamobj
        self.request.form['inputform']=None
        result=entry.MeasureDates(self.context,self.request)
        return result

class TestFormWindow(WindowTest):
    
    
    def test_valid_any_date(self):
        tested=self.build()
        #next build a fake date
        self.request.form['inputform']=None#we're overriding the database to provide a specific form
        self.assertTrue(tested.inwindow(datetime.today().date()))
        self.assertTrue(tested.inwindow(datetime(2100,11,11).date()))
        self.assertTrue(tested.inwindow(datetime(1900,11,11).date()))
        
        

class TestTeamWindow(WindowTest):
    def test_valid_any_date_legal(self):
        #first test huge range of dates with permissive team
        tested=self.build()
        self.request.form['inputform']=None
        self.assertTrue(tested.inwindow(datetime.today().date()))
        self.assertTrue(tested.inwindow(datetime(2100,11,11).date()))
        self.assertTrue(tested.inwindow(datetime(1902,12,01).date()))
    
    def test_with_start(self):
        tested=self.build()
        self.teamobj.startdate=datetime(2001,1,1).date()
        #after
        self.assertTrue(tested.inwindow(datetime(2002,1,1).date()))
        #before
        self.assertFalse(tested.inwindow(datetime(2000,1,1).date()))
        #same day
        self.assertTrue(tested.inwindow(datetime(2001,1,1).date()))
    
    def test_with_end(self):
        tested=self.build()
        self.teamobj.enddate=datetime(2010,1,1).date()
        self.assertTrue(tested.inwindow(datetime(1900,1,1).date()))
        self.assertFalse(tested.inwindow(datetime(2010,1,2).date()))
        self.assertTrue(tested.inwindow(datetime(2010,1,1).date()))
    
    def test_with_both(self):
        tested=self.build()
        self.teamobj.startdate=datetime(2008,1,1).date()
        self.teamobj.enddate=datetime(2009,1,1).date()
        self.assertTrue(tested.inwindow(datetime(2008,6,5).date()))
        self.assertFalse(tested.inwindow(datetime(2007,4,3).date()))
        self.assertFalse(tested.inwindow(datetime(2009,1,2).date()))
        self.assertTrue(tested.inwindow(datetime(2009,1,1).date()))
        self.assertTrue(tested.inwindow(datetime(2008,1,1).date()))
        
        
    
def test_suite():
   return unittest.TestSuite((
        unittest.makeSuite(TestFormWindow),
        unittest.makeSuite(TestTeamWindow)
        ))