from zope.component import createObject
from zope.formlib import form

from Products.Five.browser import BrowserView

from plone.app.form import base

from Products.qi.extranet.types.interfaces import IProject
from Products.qi import MessageFactory as _

from Products.qi.extranet.types import project as content


project_form_fields = form.Fields(IProject)

class ProjectAddForm(base.AddForm):
    """Add form for projects
    """

    form_fields = project_form_fields
    label = _(u"Add Project")
    form_name = _(u"Project settings")

    def setUpWidgets(self, ignore_request=False):

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)

    def create(self, data):
        project = createObject(u"Products.qi.Project")
        form.applyChanges(project, self.form_fields, data)
        return project

class ProjectEditForm(base.EditForm):
    """Edit form for projects
    """

    form_fields = project_form_fields

    label = _(u"Edit Project")
    form_name = _(u"Project settings")

