"""
register.py:    registration views for Projects and/or Teams in Plone 4,
                with email of project managers for respective project.

                Project notification code in part based on Products.qi
                register.cpy (skin) overrides for Plone 3.
"""

__author__ = 'Sean Upton'
__copyright__ = """
                Copyright, 2011, The University of Utah and portions
                Copyright upstream contributors.
                """.strip()
__license__ = 'GPL'


from zope.component import getUtility, getMultiAdapter


NEW_REG_SUBJ = '[%s] New User Registered'

NEW_REG_MSG = """
A new user registration related to your project is pending your approval.

A user has registered for the %s site, because they wish to
join the %s project.

The user name provided on registration is: %s

If you are a project manager, you can visit the project to search for
this user, and add them as a member of your project:

  %s


--

Please note: This is an automated notification provided by the 
%s site.
"""

from plone.app.users.browser.register import RegistrationForm
from zope.app.component.hooks import getSite
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from Products.qi.util.utils import project_containing


_PROJECT_MANAGERS = '%s-managers'


class ProjectRegistrationForm(RegistrationForm):
    """
    Custom registration form notifies project managers of new
    registrations for a project.
    """
    def _notification_subscribers(self, project):
        group = _PROJECT_MANAGERS % (self.getId())
        users = getToolByName(self.context, 'acl_users')
        listgroup = users.source_groups.listAssignedPrincipals
        return [u[0] for u in listgroup(group)] or []
    
    def _notify_project_managers(self, username):
        """Notify project managers about registration, given username"""
        portal = getSite()
        site_title = str(portal.Title())
        project = project_containing(self.context)
        project_title = str(project.Title())
        mailhost = getToolByName(project, 'MailHost')
        site = getUtility(ISiteRoot)
        recipients = self._notification_subscribers(project)
        if not recipients:
            return
        sender = site.getProperty('email_from_address')
        message = NEW_REG_MSG.strip() % ( 
            site_title,
            project_title,
            username,
            '%s/members.html' % project.absolute_url(),
            site_title,
            )
        mailhost.send(message,
                      mto=recipients,
                      mfrom=sender,
                      subject=NEW_REG_SUBJ % project_title)

    @property
    def showForm(self):
        site = getUtility(ISiteRoot)
        panel = getMultiAdapter((site, self.request),
                                name='overview-controlpanel')
        return not (panel.mailhost_warning() and
                    site.getProperty('validate_email', True))

    def handle_join_success(self, data):
        """
        Call superclass handle_join_success(), then notify project
        managers for the project in which registration was called.
        """
        RegistrationForm.handle_join_success(self, data)
        self._notify_project_managers(data['username'])

