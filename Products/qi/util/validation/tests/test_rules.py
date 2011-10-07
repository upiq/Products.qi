
import unittest

class FakeMeasure(object):
    def __init__(self):
        self.shortname='shortname'
        self.name='measurename'

class FakeTable(object):
    def get(self, *args, **kw):
        return FakeMeasure()

class FakeMeasureDB(object):
    objects=FakeTable()

class fakeDB(object):
    Measure=FakeMeasureDB()

class Base(unittest.TestCase):
    def getBuilder(self):
        from Products.qi.datacapture.validation import validationrules 
        validationrules.exp.DB=fakeDB()
        return validationrules.buildRule

class TestNumericRules(Base):
    
    def test_int_rule(self):
        build=self.getBuilder()
        rule=build('int()')
        #reminder 0=PASS no error or warning
        o={}
        self.assertEquals(rule.validate(10,o),0)
        self.assertEquals(rule.validate('10',o),0)
        self.assertEquals(rule.validate('10.1',o),10)
        self.assertEquals(rule.message, '10.1 is not a whole number')
        self.assertEquals(rule.validate(10.2,o), 10)
        self.assertEquals(rule.validate('-1',o),0)
        self.assertEquals(rule.validate('banana',o),10)
        self.assertEquals(rule.message, 'banana is not a whole number')
        self.assertEquals(rule.validate('',o),10)
        self.assertEquals(rule.validate(None,o),10)
    def test_number_rule(self):
        build=self.getBuilder()
        rule=build('number()')
        o={}
        self.assertEquals(rule.validate(10,o),0)
        self.assertEquals(rule.validate('10',o),0)
        self.assertEquals(rule.validate('10.1',o),0)
        self.assertEquals(rule.validate(10.2,o), 0)
        self.assertEquals(rule.validate('-1',o),0)
        self.assertEquals(rule.validate('banana',o),10)
        self.assertEquals(rule.message,'banana is not a number')
        self.assertEquals(rule.validate('',o),10)
        self.assertEquals(rule.validate(None,o),10)
    def test_percentage(self):
        build=self.getBuilder()
        rule=build('percent()')
        o={}
        self.assertEquals(rule.validate(.1,o),0)
        self.assertEquals(rule.validate('.1',o),0)
        self.assertEquals(rule.validate('0.1',o),0)
        self.assertEquals(rule.validate(None,o),10)
        self.assertEquals(rule.message, 'None is not a percentage value')
        self.assertEquals(rule.validate('',o),10)
        self.assertEquals(rule.validate(2,o),10)
        self.assertEquals(rule.validate(-.1,o),10)
        self.assertEquals(rule.validate(0,o),0)

class FakeValue:
    pass
class FakeOtherMeasure(object):
    def __init__(self, value):
        self.latestdate=FakeValue()
        self.latestdate.value=value

class TestEqualityRules(Base):
    def test_equals(self):
        build=self.getBuilder()
        rule=build('equals("5")')
        o={}
        self.assertEquals(rule.validate('5',o), 0)
        self.assertEquals(rule.validate('10',o),10)
        self.assertEquals(rule.validate(10,o),10)
        self.assertEquals(rule.message,'10 is not equal to 5')
        self.assertEquals(rule.validate(5,o),0)
        notEmpty={'shortname':FakeOtherMeasure(7)}
        rule=build("equals(shortname)")
        validationresult=rule.validate('7', notEmpty)
        print rule.message
        self.assertEquals(validationresult,0)
        self.assertEquals(rule.validate('6',notEmpty),10)
        self.assertEquals(rule.message,'6 is not equal to measurename')
        self.assertEquals(rule.validate('7',o),10)
    def importException(self):
        from Products.qi.datacapture.validation.rules import InvalidFunction
        return InvalidFunction
    def test_in(self):
        build=self.getBuilder()
        exceptiontype=self.importException()
        #this should fail
        try:
            rule=build('in()')
            self.fail('expected exception')
        except exceptiontype:
            pass
        rule=build('in(4,5,6.5)')
        o={}
        self.assertEquals(rule.validate(4,o),0)
        self.assertEquals(rule.validate(5,o),0)
        self.assertEquals(rule.validate(6.5,o),0)
        self.assertEquals(rule.validate(6,o),10)
        self.assertEquals(rule.validate(7,o),10)
        self.assertEquals(rule.validate('5',o),0)
        self.assertEquals(rule.validate(4.5,o),10)
        self.assertEquals(rule.validate(None,o),10)
        self.assertEquals(rule.message, 'None is not one of the following: 4, 5, 6.5')

class TestDateRules(Base):
    def test_simple_dates(self):
        build=self.getBuilder()
        o={}
        rule=build('date()')
        self.assertEquals(rule.validate('01/02/2002',o),0)
        self.assertEquals(rule.validate('06/02/2002',o),0)
        self.assertEquals(rule.validate('13/02/2002',o),10)
        self.assertEquals(rule.validate('02/29/2002',o),10)
        self.assertEquals(rule.validate('02/29/2004',o),0)
        self.assertEquals(rule.validate('01/02/02',o),10)
        self.assertEquals(rule.validate('01022002',o),10)
        self.assertEquals(rule.message, '01022002 is not a valid date (MM/DD/YYYY)')
        self.assertEquals(rule.validate('',o),10)
        self.assertEquals(rule.validate(None,o),10)
    def test_late_dates(self):
        build=self.getBuilder()
        o={}
        rule=build('afterdate("01/01/2000")')
        self.assertEquals(rule.validate('01/02/2000',o),0)
        self.assertEquals(rule.validate('12/31/1999',o),10)
        self.assertEquals(rule.message,'12/31/1999 is not after 01/01/2000')
        self.assertEquals(rule.validate('01/01/2000',o),10)
        #verify that afterdate still requires a date
        self.assertEquals(rule.validate('fake',o), 10)
    def test_early_date(self):
        build=self.getBuilder()
        o={}
        rule=build('beforedate("01/01/2000")')
        self.assertEquals(rule.validate('12/31/1999',o),0)
        self.assertEquals(rule.validate('1/5/2000',o),10)
        self.assertEquals(rule.validate('1/1/2000',o),10)
        self.assertEquals(rule.message,'1/1/2000 is not before 01/01/2000')
    
class TestComparisonRules(Base):
    def test_min_rule(self):
        build=self.getBuilder()
        o={}
        rule=build('min(5)')
        self.assertEquals(rule.validate('5',o),0)
        self.assertEquals(rule.validate(5,o),0)
        self.assertEquals(rule.validate('6',o),0)
        self.assertEquals(rule.validate(5.00001,o),0)
        self.assertEquals(rule.validate(4.9,o),10)
        self.assertEquals(rule.message,'4.9 is less than 5')
        self.assertEquals(rule.validate(-4.9,o),10)
        self.assertEquals(rule.validate('',o),10)
        self.assertEquals(rule.validate(None,o),10)
        self.assertEquals(rule.validate('carrot',o),0)
        self.assertEquals(rule.message,'carrot is not a number')
        
    def test_min_rule(self):
        build=self.getBuilder()
        o={}
        rule=build('max(5)')
        self.assertEquals(rule.validate('5',o),0)
        self.assertEquals(rule.validate(5,o),0)
        self.assertEquals(rule.validate('6',o),10)
        self.assertEquals(rule.message,'6 is larger than 5')
        self.assertEquals(rule.validate(5.00001,o),10)
        self.assertEquals(rule.validate(4.9,o),0)
        self.assertEquals(rule.validate(-4.9,o),0)
        self.assertEquals(rule.validate('',o),10)
        self.assertEquals(rule.validate(None,o),10)
        self.assertEquals(rule.validate('banana',o),10)
        self.assertEquals(rule.message,'banana is not a number')
        
        
        

def test_suite():
    return unittest.TestSuite((
         unittest.makeSuite(TestNumericRules),
         unittest.makeSuite(TestEqualityRules),
         unittest.makeSuite(TestDateRules),
         unittest.makeSuite(TestComparisonRules),
         ))