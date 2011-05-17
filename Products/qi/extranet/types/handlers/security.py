from Products.CMFCore.utils import getToolByName
from Products.qi.util.logger import logger


def add_project_security(project, event):
    # create groups related to the project at project add time
    wftool = getToolByName(project, 'portal_workflow')
    wftool.doActionFor(project, 'publish')
    
    
    acl_users = getToolByName(project, 'acl_users')
    source_groups = acl_users.source_groups
    proj_id = project.getId()
    proj_title = project.title or proj_id
    try:
        for suffix in ('members', 'faculty', 'contributors', 'managers','pending','qics'):
            group_name = '%s-%s' % (proj_id, suffix)
            source_groups.addGroup(
                group_name, '%s project %s' % (proj_title, suffix)
                )
        # add the faculty group to the contributors group
        source_groups.addPrincipalToGroup('%s-faculty' % proj_id,
                                          '%s-contributors' % proj_id)
    
        settings = [
            {'type':'group', 'id':'%s-managers' % proj_id,
             'roles':[u'Contributor', u'Editor', u'Reader', u'Reviewer',
                      u'Manager']},
            {'type':'group', 'id':'%s-faculty' % proj_id,
             'roles':[u'Reader']},
            {'type':'group', 'id':'%s-members' % proj_id,
             'roles':[u'ProjectViewer']},
            {'type':'group', 'id':'%s-qics' % proj_id,
            'roles':[u'QIC']},
            {'type':'group', 'id':'%s-contributors' % proj_id,
             'roles':[u'Contributor', u'Editor', u'Reader']},
            # no proj-member roles here, nor anonymous roles
            ]

        _secure_content(project, project, settings, False)
    except KeyError:
        pass



def add_team_security(team, event):
    # create groups related to the project at project add time
    #wftool = getToolByName(team, 'portal_workflow')
    #wftool.doActionFor(team, 'publish')
    print "adding team security for %s"%team.title
    acl_users = getToolByName(team, 'acl_users')
    source_groups = acl_users.source_groups
    project=event.newParent.getProject()
    try:
        parentTeam=event.newParent.getTeam()
    except AttributeError:
        parentTeam=None
    project_id=project.getId()
    project_title=project.title or project_id
    team_id = team.getId()
    team_title = team.title or team_id
    
    for suffix in ('members', 'lead'):
        try:
            group_name = project.getProjectGroup('%s-%s' % (team_id, suffix))
            source_groups.addGroup(
                group_name, '%s team %s' % (team_title, suffix)
                )

        except KeyError,e:
            logger.handleException(e)
            #do nothing the group already exists(created, deleted, recreated e.g.)
            pass
    viewerName="TeamViewer"
    if parentTeam is not None:
        viewerName=u"SubTeamViewer"
    settings = [
        {'type':'group', 'id':'%s-%s-lead' % (project_id,team_id),
         'roles':[u'Contributor', u'Editor', u'Reader', u'Reviewer',
                  u'Manager', viewerName]},
        {'type':'group', 'id':'%s-%s-members' % (project_id,team_id),
         'roles':[viewerName,]},
                  
        # no proj-member roles here, nor anonymous roles
        ]
    _secure_content(team, team, settings, False)


    
def _secure_content(project, content, settings, inherit):
    request = getattr(project, 'REQUEST', None)
    from plone.app.workflow.browser.sharing import SharingView
    wftool = getToolByName(project, 'portal_workflow')
    chain = wftool.getChainFor(content)
    wf = wftool.getWorkflowById(chain[0])
    sharing_view = SharingView(content, request)
    sharing_view.update_inherit(True)
    sharing_view.update_role_settings(settings)


