from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME


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
