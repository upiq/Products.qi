from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME


def setProjectSkin(obj, event):
    #print vars(event)
    other=event.request.other
    try:
        lastparent=other['PARENTS'][-1]
        objectname=other['TraversalRequestNameStack'][-1]
    except:
        return
    if hasattr(lastparent, objectname):
        realobj=getattr(lastparent,objectname)
        if hasattr(realobj,'projectTheme'):
            theme=realobj.projectTheme
            obj.changeSkin(theme,event.request)


def manage_project_logo(project, event):
    # bounce the formdata .logo field over to a logo subobject on add or edit
    if project.logo:
        tt = getattr(project, 'portal_types')
        image = getattr(project, _PROJECT_LOGO_NAME, None)
        if image is None:
            theid = tt.constructContent('Image', project, _PROJECT_LOGO_NAME)
            image = getattr(project, theid)
        image.update_data(project.logo)
        project.logo = ''
    return project
