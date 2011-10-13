#rethink this
def add_managers(project, changeevent):
    managers=project.managers
    plugin = project.acl_users.source_groups
    
    
    group_id = project.getProjectGroup('managers')
    group= plugin.getGroup(group_id)
    for oldmember in group.getMemberIds():
        group.removeMember(oldmember)
    for email in managers:
        plugin.addPrincipalToGroup(email, group_id)


def add_leads(team, changeevent):
    managers=team.managers
    if hasattr(team, 'getProject'):
        project=team.getProject()
    elif hasattr(event.newParent,'getProject'):
        project=event.newParent.getProject()
    else:
        return
    plugin = project.acl_users.source_groups    
    group_id = team.getGroup('lead')
    group= plugin.getGroupById(group_id)
    for oldmember in group.getMemberIds():
        group.removeMember(oldmember)
    for email in managers:
        plugin.addPrincipalToGroup(email, group_id)
