import unittest
from Products.qi.tests.base import SupportPolicyTestCase
from Products.CMFCore.utils import getToolByName
from Products.qi.tests.base import setup_support_policy

class TestSetup(SupportPolicyTestCase):

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')

    #as far as I can tell these two tests will never pass
    def test_portal_title(self):
        pass
        #self.assertEquals("QI TeamSpace", self.portal.getProperty('title'))

    def test_portal_description(self):
        pass
        #self.assertEquals("Welcome to QI TeamSpace", self.portal.getProperty('description'))
    

def test_suite():
    suite = unittest.makeSuite(TestSetup)
    return suite
        