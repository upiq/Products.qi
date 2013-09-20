from plone.uuid.interfaces import IAttributeUUID
from plone.directives import form
from plone.namedfile import field as filefield
from plone.namedfile.interfaces import HAVE_BLOBS
from z3c.form.converter import TextLinesConverter
from z3c.form.browser import textlines
from zope.interface import Interface, Invalid, invariant
from zope.container.interfaces import IOrderedContainer
from zope import schema

from Products.qi import MessageFactory as _
from uu.smartdate.browser.widget import SmartdateFieldWidget


NamedImage = filefield.NamedImage
if HAVE_BLOBS:
    NamedImage = filefield.NamedBlobImage


# package constants for FTI portal_type names:
PROJECT_TYPE = 'qiproject'
TEAM_TYPE = 'qiteam'
SUBTEAM_TYPE = 'qisubteam'
WORKSPACE_TYPES = (PROJECT_TYPE, TEAM_TYPE, SUBTEAM_TYPE)


class UTF8LinesConverter(TextLinesConverter):
    """
    lines converter for (assumed utf-8 encoded) List of BytesLine field.
    Useful for lists of textual strings (e.g. email addresses and identifiers)
    that are not natively Unicode strings, but may optionally be extended
    by encodings (though values for these are usually ASCII, casting alone
    should be considered too implicit and too prone to break).
    """

    def toWidgetValue(self, value):
        if value and isinstance(value[0], str):
            value = list(element.decode('utf-8') for element in value)
        return super(UTF8LinesConverter, self).toWidgetValue(value)

    def toFieldValue(self, value):
        collection_type = self.field._type
        value_type = self.field.value_type._type
        lines = super(UTF8LinesConverter, self).toFieldValue(value)
        if lines is not None and value_type is str:
            return collection_type(element.encode('utf-8') for element in lines)
        return lines  # default unicode values


class IWorkspace(form.Schema, IOrderedContainer, IAttributeUUID):
    """
    A workspace is a folder for use as or in a project. A
    workspace may have its own designated membership and
    user-groups associated with it (these abilities should
    be accomplished via adaptation -- this interface does
    not mandate a specific interface for handling that).
    """

    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Workspace name or display title.'),
        required=True)

    description = schema.Text(
        title=_(u'Description'),
        description=(u'Project description; may be displayed for viewers '
                     u'of project.'),
        required=False,
        )

    form.widget(start=SmartdateFieldWidget)
    start = schema.Date(
        title=_(u'Start date'),
        description=_(u'Date collaboration in workspace is to begin.'),
        required=False,
        )

    form.widget(end=SmartdateFieldWidget)
    end = schema.Date(
        title=_(u'End date'),
        description=_(u'Date collaboration in workspace is to end.'),
        required=False,
        )


class IProject(IWorkspace):
    """
    Project is a top-level folder with project workspace.
    """

    form.fieldset(
        'configuration',
        label=_(u'Configuration'),
        fields=['start', 'end', 'contacts', 'logo'],
        )

    form.widget(contacts=textlines.TextLinesFieldWidget)
    contacts = schema.List(
        title=_(u'Contact email'),
        description=_(u'Project contact email addresses, one per line.'),
        value_type=schema.BytesLine(required=False),
        defaultFactory=list,    # requires zope.schema >= 3.8.0
        required=False,
        )

    logo = NamedImage(
        title=_(u'Project logo'),
        description=_(u'Upload a project logo file as PNG or JPEG image.'),
        required=False,
        )

    @invariant
    def start_end_valid_range(data):
        if data.end and data.start:
            if data.start > data.end:
                raise Invalid('Start after end: invalid date range')


class ITeam(IWorkspace):
    """Marker for any kind of team (including sub-team) workspace"""

    form.fieldset(
        'configuration',
        label=_(u'Configuration'),
        fields=['start', 'end'],
        )


class ISubTeam(ITeam):
    """Marker for a specifically sub-team workspace"""


class IWorkspaceContext(Interface):
    """
    Adapter interface providing the workspace context for projects and
    teams, given some location being adapted.
    """

    def team():
        """
        Return containing team workspace for context or None
        """

    def project():
        """
        Return containing project workspace for context or None
        """

    def workspace():
        """
        Return containing project or team workspace for context or None.
        If there is a team context, return that in preference to outer
        containing project.
        """

