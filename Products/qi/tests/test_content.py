import unittest

class ProjectTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.qi.extranet.types.project import Project
        return Project

    def _makeOne(self, id='test', *args, **kw):
        return self._getTargetClass()(id=id, *args, **kw)

    def test_class_conforms_to_IQIProject(self):
        from zope.interface.verify import verifyClass
        from Products.qi.extranet.types.interfaces import IQIProject
        verifyClass(IQIProject, self._getTargetClass())

    def test_class_conforms_to_ISelectableBrowserDefault(self):
        from zope.interface.verify import verifyClass
        from Products.CMFDynamicViewFTI.interface \
            import ISelectableBrowserDefault
        verifyClass(ISelectableBrowserDefault, self._getTargetClass())

    def test_HEAD_no_fti(self):
        from zExceptions import NotFound
        request = DummyRequest()
        response = DummyResponse()
        project = self._makeOne()
        self.assertRaises(NotFound, project.HEAD, request, response)

    def test_HEAD_w_fti_no_view_method(self):
        from zExceptions import NotFound
        request = DummyRequest()
        response = DummyResponse()
        project = self._makeOne()
        project.getTypeInfo = lambda: DummyFTI()
        self.assertRaises(NotFound, project.HEAD, request, response)

    def test_HEAD_w_fti_view_method_no_HEAD(self):
        from zExceptions import MethodNotAllowed
        request = DummyRequest()
        response = DummyResponse()
        project = self._makeOne()
        project.getTypeInfo = lambda: DummyFTI()
        project.dummy = object()
        self.assertRaises(MethodNotAllowed, project.HEAD, request, response)

    def test_HEAD_w_fti_view_method_w_HEAD(self):
        request = DummyRequest()
        response = DummyResponse()
        project = self._makeOne()
        project.getTypeInfo = lambda: DummyFTI()
        project.dummy = DummyViewMethod()
        self.assertEqual(project.HEAD(request, response), 'Dummy HEAD')

class TeamTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.qi.extranet.types.team import Team
        return Team

    def _makeOne(self, id='test', *args, **kw):
        return self._getTargetClass()(id=id, *args, **kw)

    def test_class_conforms_to_IQITeam(self):
        from zope.interface.verify import verifyClass
        from Products.qi.extranet.types.interfaces import IQITeam
        verifyClass(IQITeam, self._getTargetClass())

    def test_class_conforms_to_ISelectableBrowserDefault(self):
        from zope.interface.verify import verifyClass
        from Products.CMFDynamicViewFTI.interface \
            import ISelectableBrowserDefault
        verifyClass(ISelectableBrowserDefault, self._getTargetClass())

    def test_HEAD_no_fti(self):
        from zExceptions import NotFound
        request = DummyRequest()
        response = DummyResponse()
        project = self._makeOne()
        self.assertRaises(NotFound, project.HEAD, request, response)

    def test_HEAD_w_fti_no_view_method(self):
        from zExceptions import NotFound
        request = DummyRequest()
        response = DummyResponse()
        team = self._makeOne()
        team.getTypeInfo = lambda: DummyFTI()
        self.assertRaises(NotFound, team.HEAD, request, response)

    def test_HEAD_w_fti_view_method_no_HEAD(self):
        from zExceptions import MethodNotAllowed
        request = DummyRequest()
        response = DummyResponse()
        team = self._makeOne()
        team.getTypeInfo = lambda: DummyFTI()
        team.dummy = object()
        self.assertRaises(MethodNotAllowed, team.HEAD, request, response)

    def test_HEAD_w_fti_view_method_w_HEAD(self):
        request = DummyRequest()
        response = DummyResponse()
        team = self._makeOne()
        team.getTypeInfo = lambda: DummyFTI()
        team.dummy = DummyViewMethod()
        self.assertEqual(team.HEAD(request, response), 'Dummy HEAD')


class DummyRequest:
    pass

class DummyResponse:
    pass

class DummyFTI:
    def getDefaultPage(self, context, check_exists=False):
        return 'dummy'

class DummyViewMethod:
    def __of__(self, other):
        return self

    def HEAD(self, REQUEST, RESPONSE):
        return 'Dummy HEAD'

def test_suite():
    return unittest.makeSuite(ProjectTests)
