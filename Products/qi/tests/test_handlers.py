import unittest

class TestManageProjectLogo(unittest.TestCase):
    def _getFUT(self):
        from Products.qi.extranet.types.handlers.lookandfeel import manage_project_logo
        return manage_project_logo

    def _makeProject(self):
        project = DummyProject()
        project.portal_types = DummyTypesTool()
        return project

    def test_add_nologo(self):
        manage_project_logo = self._getFUT()
        from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
        project = self._makeProject()
        event = None
        project = manage_project_logo(project, event)
        self.assertEqual(project.logo, '')
        self.failIf(hasattr(project, _PROJECT_LOGO_NAME))

    def test_add_logo(self):
        manage_project_logo = self._getFUT()
        from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
        project = self._makeProject()
        project.logo = 'thelogo'
        event = None
        project = manage_project_logo(project, event)
        self.assertEqual(project.logo, '')
        self.assertEqual(getattr(project, _PROJECT_LOGO_NAME).data, 'thelogo')

    def test_edit_nologo(self):
        manage_project_logo = self._getFUT()
        from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
        project = self._makeProject()
        image = DummyContent()
        setattr(project, _PROJECT_LOGO_NAME, image)
        event = None
        project = manage_project_logo(project, event)
        self.assertEqual(project.logo, '')
        self.assertEqual(getattr(project, _PROJECT_LOGO_NAME).data, None)

    def test_edit_logo(self):
        manage_project_logo = self._getFUT()
        from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
        project = self._makeProject()
        image = DummyContent()
        setattr(project, _PROJECT_LOGO_NAME, image)
        project.logo = 'thelogo'
        event = None
        project = manage_project_logo(project, event)
        self.assertEqual(project.logo, '')
        self.assertEqual(getattr(project, _PROJECT_LOGO_NAME).data, 'thelogo')

class AddProjectSecurityTests(unittest.TestCase):
    def _getFUT(self):
        from Products.qi.extranet.types.handlers.security import add_project_security
        return add_project_security

    def test_it(self):
        project = DummyProject()
        project.acl_users = DummyPAS()
        project.portal_workflow = DummyWorkflowTool()
        project.portal_membership = DummyMembershipTool()
        add_project_group = self._getFUT()
        add_project_group(project, None)
        self.assertEqual(len(project.acl_users.groups), 6)
        i = 0
        for group_name in ('members', 'faculty', 'contributors', 'managers','pending','qics'):
            name, title = project.acl_users.groups[i]
            self.assertEqual(name, 'myproject-%s' % group_name)
            self.assertEqual(title, 'My Project project %s' % group_name)
            i += 1
        self.assertEqual(len(project.acl_users.principals_to_groups), 1)
        princ_id, group_id = project.acl_users.principals_to_groups[0]
        self.assertEqual(princ_id, 'myproject-faculty')
        self.assertEqual(group_id, 'myproject-contributors')
        #we have a data entry role as well now
        self.assertEqual(len(project.localrole_info), 5)



class DummyTypesTool:
    def constructContent(self, type, container, name, **kw):
        image = DummyContent()
        image.portal_membership = DummyMembershipTool()
        setattr(container, name, image)
        return name

class State:
    id = 'published'
    def getId(self):
        return self.id

class Workflow:
    def _getWorkflowStateOf(self, context):
        return State()

class DummyMembershipTool:
    def checkPermission(self, *arg):
        return True

class DummyWorkflowTool:
    def doActionFor(self, ob, transition):
        self.ob = ob
        self.transition = transition

    def getChainFor(self, ob):
        return [0]

    def getWorkflowById(self, id):
        return Workflow()

class DummyContent:
    data = None
    id = 'content'

    def __init__(self):
        self.localrole_info = []
        
    def update_data(self, data):
        self.data = data

    def reindexObjectSecurity(self, *arg):
        pass

    def getId(self):
        return self.id

    def get_local_roles_for_userid(self, *arg, **kw):
        return []

    def manage_setLocalRoles(self, user_id, roles):
        self.localrole_info.append((user_id, roles))

class DummyProject(DummyContent):
    logo = ''
    title = 'My Project'
    id = 'myproject'

class DummyPAS:
    def __init__(self):
        self.source_groups = self
        self.groups = []
        self.principals_to_groups = []

    def addGroup(self, group_id, group_title):
        self.groups.append((group_id, group_title))

    def addPrincipalToGroup(self, principal_id, group_id):
        self.principals_to_groups.append((principal_id, group_id))

class DummyRequest:
    pass
    
def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])
