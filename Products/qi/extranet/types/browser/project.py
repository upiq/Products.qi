
from zope.component import createObject
from zope.formlib import form

from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility

from Acquisition import aq_inner
from zExceptions import BadRequest
from Products.Five.browser import BrowserView
from Products.qi.util.general import BrowserPlusView
from Products.CMFCore.utils import getToolByName
from plone.portlets.manager import PortletManager
from DateTime import DateTime

from plone.app.form import base
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
#from plone.app.vocabularies.users import UsersSource
from Products.qi.extranet.users.qiuser import QiUsersSource as UsersSource
from plone.app.vocabularies.users import UsersSourceQueryView

from Products.qi.extranet.types.interfaces import IQIProject
from Products.qi import MessageFactory as _
from Products.qi.extranet.types.handlers.users import add_managers_and_faculty
from qi.sqladmin.models import Project as RelProject
from qi.sqladmin import models as DB
from datetime import datetime

from Products.qi.extranet.types.handlers import django as dbhandlers
from Products.qi.extranet.types import project as content
from Products.qi.util.utils import getTeamsInContext
from Products.CMFPlone.patches.unicodehacks import _unicode_replace
from Products.qi.util import utils


project_form_fields = form.Fields(IQIProject)
#project_form_fields['managers'].custom_widget = UberMultiSelectionWidget
#project_form_fields['faculty'].custom_widget = UberMultiSelectionWidget

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

 
class Synchronize(BrowserView):
    def __call__(self, *args, **kw):
        project=self.context
        if not isinstance(project, content.Project):
            raise Exception
        dbhandlers.persistProjectToDjango(project, None)
        for child in project.getChildNodes():
            if isinstance(child, content.Team):
                dbhandlers.persistTeamToDjango(child,None)
        self.request.response.redirect(self.context.absolute_url())
    
    
    
