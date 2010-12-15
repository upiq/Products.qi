"""
register.py:    registration views for Projects and/or Teams in Plone 4,
                with email of project managers for respective project.

                Project notification code in part based on Products.qi
                register.cpy (skin) overrides for Plone 3.
"""

__author__ = 'Sean Upton'
__copyright__ = """
                Copyright, 2010, The University of Utah and
                QI Teamspace Developers
                """.strip()
__license__ = 'GPL'


from zope.component import getUtility, getMultiAdapter


from Products.qi.util import PLONE_VERSION


NEW_REG_SUBJ = '[QI Teamspace] New User Registered'

NEW_REG_MSG = """
A new user registration related to your project is pending your approval.

A user has registered for the QI Teamspace site, because they wish to
join the %s project.

The user name provided on registration is: %s

If you are a project manager, you can visit the project to search for
this user, and add them as a member of your project:

  %s


--

(This message is an automated notification provided by QI Teamspace).
"""


if PLONE_VERSION == 3:
    from Products.Five.browser import BrowserView
    class ProjectRegistrationForm(BrowserView):
        """Here to keep registration from breaking in Plone 3."""
        def __call__(self):
            """
            Just redirect back to the object for which the view was called.
            """
            goto_url = aq_parent(aq_inner(self.context)).absolute_url()
            return self.request.response.redirect(goto_url)

else:
    # Plone 4.x+
    from plone.app.users.browser.register import RegistrationForm
    from Products.CMFCore.interfaces import ISiteRoot
    from Products.CMFCore.utils import getToolByName

    class ProjectRegistrationForm(RegistrationForm):
        """
        Custom registration form notifies project managers of new
        registrations for a project.
        """
        def _notification_subscribers(self, project):
            users = getToolByName(self.context, 'acl_users')
            if hasattr(self.context, 'ProjectEmail'):
                return self.context.ProjectEmail
            else:
                addr = lambda u: users.getUserById(u).getProperty('email')
                managers = project.getProjectUsers('managers')
                return [addr(u) for u in managers]

        def _notify_project_managers(self, username):
            """Notify project managers about registration, given username"""
            project = self.context.getProject()
            mailhost = getToolByName(self.context, 'MailHost')
            #site = getToolByName(self.context, 'portal_url').getPortalObject()
            site = getUtility(ISiteRoot)
            recipients = self._notification_subscribers(project)
            if not recipients:
                return
            sender = site.getProperty('email_from_address')
            message = NEW_REG_MSG.strip() % ( 
                str(project.title),
                username,
                '%s/members.html' % project.absolute_url(),)
            mailhost.send(message,
                          mto=recipients,
                          mfrom=sender,
                          subject=NEW_REG_SUBJ)

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
