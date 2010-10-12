from Products.CMFCore.utils import getToolByName
from Products.qi.util.utils import get_factory_permission
from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
from zExceptions import BadRequest
from threading import Semaphore
from Products.qi.mail.newListener import MailListener, imapEnabled
from threading import currentThread
#from Products.qi.datacapture.file.uploads import UploadThread
from Products.qi.util.logger import logger


def addManagersAndFacultyAsMembers(project, event):
    managers=project.managers
    faculty=project.faculty
    added=[k for k in managers]
    added[len(added):]=faculty
    plugin = project.acl_users.source_groups
    for email in added:
        group_id = project.getProjectGroup()
        plugin.addPrincipalToGroup(email, group_id)


def addLeadsAsMembers(team, event):
    leads=team.managers
    if hasattr(team, 'getProject'):
        project=team.getProject()
    else:
        project=event.newParent.getProject()
    plugin = project.acl_users.source_groups
    for email in leads:
        group_id = project.getProjectGroup()
        team_group_id = team.getGroup()
        plugin.addPrincipalToGroup(email, group_id)
        plugin.addPrincipalToGroup(email, team_group_id)

#rethink this
def add_managers_and_faculty(project, changeevent):
    managers=project.managers
    faculty=project.faculty
    plugin = project.acl_users.source_groups
    
    
    group_id = project.getProjectGroup('managers')
    group= plugin.getGroup(group_id)
    for oldmember in group.getMemberIds():
        group.removeMember(oldmember)
    for email in managers:
        plugin.addPrincipalToGroup(email, group_id)
        
    group_id = project.getProjectGroup('faculty')
    group= plugin.getGroup(group_id)
    for oldmember in group.getMemberIds():
        group.removeMember(oldmember)
    for email in faculty:
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