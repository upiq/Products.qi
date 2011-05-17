from Products.CMFCore.utils import getToolByName
from Products.qi.util.utils import get_factory_permission


def enable_addable_types(project, event):
    """
    Give the given role the add permission on all the selected types.
    """
    portal_types = getToolByName(project, 'portal_types')
    role = 'TeamMember'
    
    for fti in portal_types.listTypeInfo():
        type_id = fti.getId()
        permission = get_factory_permission(project, fti)
        if permission is not None:
            roles = [r['name'] for r in project.rolesOfPermission(permission)
                        if r['selected']]
            acquire = bool(project.permission_settings(permission)[0]['acquire'])
            if type_id in project.addable_types and role not in roles:
                roles.append(role)
            elif type_id not in project.addable_types and role in roles:
                roles.remove(role)
            project.manage_permission(permission, roles, acquire)

