from security import _secure_content


from Products.CMFCore.utils import getToolByName
from Products.qi.util.utils import get_factory_permission
from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
from zExceptions import BadRequest
from threading import Semaphore
from Products.qi.mail.newListener import MailListener, imapEnabled
from threading import currentThread
from Products.qi.datacapture.file.uploads import UploadThread
from Products.qi.util.logger import logger

def enable_addable_types(project, event):
    """Give the given role the add permission on all the selected types.
    """
    portal_types = getToolByName(project, 'portal_types')
    role = 'TeamMember'
    
    for fti in portal_types.listTypeInfo():
        type_id = fti.getId()

        permission = get_factory_permission(project, fti)
        if permission is not None:
            roles = [r['name'] for r in project.rolesOfPermission(permission) if r['selected']]
            acquire = bool(project.permission_settings(permission)[0]['acquire'])
            if type_id in project.addable_types and role not in roles:
                roles.append(role)
            elif type_id not in project.addable_types and role in roles:
                roles.remove(role)
            project.manage_permission(permission, roles, acquire)


    

    
def add_project_content(project, event):
    return
    #not sure we want this anymore
    request = getattr(project, 'REQUEST')
    tt = getattr(project, 'portal_types')
    try:
        tt.constructContent('Folder', project, 'docs', title='Documents')
        tt.constructContent('Folder', project, 'about', title='About')
    except BadRequest:
        pass
    proj_id = project.getId()
    for content, settings in (

        [project.docs,
          [ {'type':'group', 'id':'%s-managers' % proj_id,
             'roles':[u'Contributor', u'Editor', u'Reader', u'Reviewer',
                      u'Manager']},
            {'type':'group', 'id':'%s-faculty' % proj_id,
             'roles':[u'Reader']},
            {'type':'group', 'id':'%s-contributors' % proj_id,
             'roles':[u'Contributor', u'Editor', u'Reader']},
            {'type':'group', 'id':'%s-members' % proj_id,
             'roles':[u'Reader']},
            ],
         ],

        [project.about,
          [ {'type':'group', 'id':'%s-managers' % proj_id,
             'roles':[u'Contributor', u'Editor', u'Reader', u'Reviewer',
                      u'Manager']},
            {'type':'group', 'id':'%s-faculty' % proj_id,
             'roles':[u'Reader']},
            {'type':'group', 'id':'%s-contributors' % proj_id,
             'roles':[u'Contributor', u'Editor', u'Reader']},
            {'type':'group', 'id':'%s-members' % proj_id,
             'roles':[u'Reader']},
            {'type':'user', 'id':'Anonymous User',
             'roles':[u'Reader']},
            ],
         ],

       ):
         _secure_content(project, content, settings, False)
         

from Products.qi.util.logger import projectlog as log
def recordProjectChange(project, change):
    log.logText('%s was changed'%project)
    history=project.workflow_history['qi_project_workflow']
    for x in history:
        log.logText('\t%s (%s): %s'%(x['actor'],x['time'],x['action']))


