import unittest



class ProjectMembersTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.qi.extranet.users.browser.managemembers import TeamMembersView
        return TeamMembersView

    def _makeOne(self, context=None, request=None):
        if context is None:
            context = object()
        if request is None:
            request = {}
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IBrowserView(self):
        from zope.interface.verify import verifyClass
        from zope.publisher.interfaces.browser import IBrowserView
        verifyClass(IBrowserView, self._getTargetClass())

    def test_instance_conforms_to_IBrowserView(self):
        from zope.interface.verify import verifyObject
        from zope.publisher.interfaces.browser import IBrowserView
        verifyObject(IBrowserView, self._makeOne())

    def test_listProjectMembers_empty_group(self):
        project = DummyProject()
        project.portal_membership = DummyMembershipTool()
        view = self._makeOne(project)
        members = view.listProjectMembers()
        self.assertEqual(len(members), 0)

    def test_listProjectMembers_non_empty_group(self):
        groups = {'dummy-members': ('fred', 'wilma')}
        project = DummyProject(groups)
        project.portal_membership = DummyMembershipTool(
                                        fred='Fred Flintstone',
                                        wilma='Wilma Flintstone',
                                        )
        view = self._makeOne(project)
        members = view.listProjectMembers()
        self.assertEqual(len(members), 2)
        ids = [x['id'] for x in members]
        self.failUnless('fred' in ids)
        self.failUnless('wilma' in ids)
        names = [x['name'] for x in members]
        self.failUnless('Fred Flintstone' in names)
        self.failUnless('Wilma Flintstone' in names)

    def test_addNewUser(self):
        groups = {'dummy-members': []}
        project = DummyProject(groups)
        reg = project.portal_registration = DummyRegistrationTool(
                                                    project.acl_users)
        mtool = project.portal_membership = DummyMembershipTool()
        mtool.names['barney@bedrock.com'] = 'Barney Rubble'
        view = self._makeOne(project)

        view.addNewUser(email='barney@bedrock.com',
                        password='yabba',
                        full_name='Barney Rubble',
                       )

        self.assertEqual(reg.called_with['id'], 'barney@bedrock.com')
        self.assertEqual(reg.called_with['password'], 'yabba')
        self.assertEqual(reg.called_with['roles'], ('Member',))
        self.assertEqual(reg.called_with['domains'], '')
        self.assertEqual(reg.called_with['properties'],
                         {'fullname': 'Barney Rubble',
                          'email': 'barney@bedrock.com',
                          'username': 'barney@bedrock.com',
                         })

        members = view.listProjectMembers()
        self.assertEqual(len(members), 1)
        ids = [x['id'] for x in members]
        self.failUnless('barney@bedrock.com' in ids)
        names = [x['name'] for x in members]
        self.failUnless('Barney Rubble' in names)

class DummyGroupsPlugin:

    def __init__(self, groups):
        self.groups = groups.copy()

    def listAssignedPrincipals(self, group_id):
        users = self.groups.get(group_id, ())
        return [(id, id) for id in users]

    def addPrincipalToGroup( self, principal_id, group_id, REQUEST=None ):
        users = list(self.groups[group_id])
        print self.groups
        if principal_id in users:
            raise ValueError('Dupe!')
        users.append(principal_id)
        self.groups[group_id] = tuple(users)

class DummyMember:
    def __init__(self, name, id):
        self.name=name
        self.id=id
    def getProperty(self, property):
        if property=='fullname':
            return name
        else: 
            return id
    pass

class DummyMembershipTool:

    def __init__(self, **kw):
        self.names = kw.copy()

    def getMemberInfo(self, id):
        return {'fullname': self.names[id]}
        
    def getMemberById(self, id):
        return DummyMember(name=self.names[id],id=id)


class DummyRegistrationTool:

    called_with = None

    def __init__(self, user_folder):
        self.user_folder = user_folder

    def addMember(self, id, password, roles=('Member',), domains='',
                  properties=None, REQUEST=None):
        self.called_with = {'id': id,
                            'password': password,
                            'roles': roles,
                            'domains': domains,
                            'properties': properties,
                           }

class DummyUserFolder:

    def __init__(self, groups):
        self.source_groups = DummyGroupsPlugin(groups)


class DummyProject:

    def __init__(self, groups=None):
        self._id = 'dummy'
        if groups is None:
            groups = {}
        uf = self.acl_users = DummyUserFolder(groups)

    def getId(self):
        return self._id
    
    def getGroup(self,arg="members"):
        return self.getProjectGroup(arg)
    
    def getProjectGroup(self, arg='members'):
        return 'dummy-'+arg


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ProjectMembersTests),
    ))
