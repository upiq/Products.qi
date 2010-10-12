import unittest

from mockdjango import MockDB, MockTable, MockDjangoObject

class MockContext:
    def __init__(self):
        self.request=MockRequest()
    def absolute_url(self):
        return "example.com"
        

class MockRequest:
    def __init__(self):
        self.response=MockResponse()
        self.RESPONSE=self.response
        self.form=MockForm()
    def __setitem__(self, arg, arg2):
        pass
class MockForm(dict):
    pass
class MockResponse:
    pass


class MockMeasure(MockTable):
    pass

class MockMeasureObject(MockDjangoObject):
    pass

class MockTeam(MockTable):
    pass
class MockTeamObject(MockDjangoObject):
    pass

class MockMeasureValue(MockTable):
    pass
class MockMeasureValueObject(MockDjangoObject):
    pass

class ChartTest(unittest.TestCase):
    
    def setUp(self):
        from Products.qi.report.internal.browser.charts import charts
        self.oldDB=charts.DB
        self.django=MockDB()
        charts.DB=self.django
        
    def tearDown(self):
        from Products.qi.report.internal.browser.charts import charts
        charts.DB=self.oldDB
        
    
    def _getTestedClass(self):
        from Products.qi.report.internal.browser.charts  import charts
        #modify the data source as necessary

        return charts.ChartData
    
    def _build(self):
        _built=self._getTestedClass()
        context=MockContext()
        return _built(context,context.request)
    
    def test_exists(self):
        built=self._build()
        self.assertTrue(built is not None)
    
    def test_normal_set(self):
        tested=self._build()
        tested.context.request.form['measureid']=1
        self.django.Measure=MockMeasure()
        self.django.Team=MockTeam()
        self.django.MeasurementValue=MockMeasureValue()
        data=tested.Set(1)
        self.assertEqual(len(data),0)
        self.django.MeasurementValue.objects.rows=[MockMeasureValueObject(),MockMeasureValueObject()]
        self.assertEqual(len(data),2)
            
        
        
def test_suite():
    return unittest.TestSuite(
        (unittest.makeSuite(ChartTest))
    )