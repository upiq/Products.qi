
import unittest
from datetime import datetime

class FakeSet:
    def filter(self,*args,**kw):
        return self.returnedSet
    def get(self,*args, **kw):
        return self.getval
    def order_by(self,*args,**kw):
        return self.returnedSet

class FakeMeasureValue:
    objects=FakeSet()
class FakeMeasureChange:
    objects=FakeSet()
    
    def __init__(self, value=None,annotation=None):
        if value is not None:
            self.oldvalue=value
        if annotation is not None:
            self.oldannotation=annotation

class FakeContext:
    objects=FakeSet()
    def getDBTeam(self):
        return self.dbteamobj
    

class FakeRequest:
    pass

class TestSuppression(unittest.TestCase):
    def create(self):
        from Products.qi.datacapture.rawdata.browser import history
        history.DB.MeasurementValue=FakeMeasureValue
        history.DB.MeasurementChange=FakeMeasureChange
        self.context=FakeContext()
        self.request=FakeRequest()
        self.request=self.request
        result=history.HistoryView(self.context,self.request)
        self.request.form={}
        return result
    
    def test_simple_set(self):
        results=[]
        fakeset=FakeSet()
        FakeMeasureChange.objects.returnedSet=fakeset
        fakeset.returnedSet=results
        FakeMeasureValue.objects.getval=FakeMeasureValue()
        
        tested=self.create()
        self.assertEquals(len(tested.history()),0)
        results=[FakeMeasureValue()]
        fakeset=FakeSet()
        FakeMeasureChange.objects.returnedSet=fakeset
        fakeset.returnedSet=results
        self.assertEquals(len(tested.history()),1)
    
    def test_duplicate_elimination(self):
        tested=self.create()
        FakeMeasureValue.objects.getval=FakeMeasureValue()
        results=[FakeMeasureChange(1,'test note'),
            FakeMeasureChange(2,'test note'),
            FakeMeasureChange(1,'test note'), 
            FakeMeasureChange(1,'test note')]
        fakeset=FakeSet()
        FakeMeasureChange.objects.returnedSet=fakeset
        fakeset.returnedSet=results
        self.assertEquals(len(tested.history()),3)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSuppression),
        ))