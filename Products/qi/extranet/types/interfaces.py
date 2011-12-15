from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.uuid.interfaces import IAttributeUUID
from plone.directives import form
from plone.namedfile import field as filefield
from plone.namedfile.interfaces import HAVE_BLOBS
from zope.interface import Interface
from zope.container.interfaces import IOrderedContainer
from zope import schema

from Products.qi import MessageFactory as _


NamedImage = filefield.NamedImage
if HAVE_BLOBS:
    NamedImage = filefield.NamedBlobImage



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
        description=_(u'Project name or display title.'),
        required=True)
    
    description = schema.Text(
        title=_(u'Description'),
        description=(u'Project description; may be displayed for viewers '\
                     u'of project.'),
        required=False,
        )
    
    def getId():
        """Return the id fo the workspace as a string"""


class IProject(IWorkspace, INavigationRoot):
    """
    Project is a folder with project workspace that is also
    an INavigationRoot.
    """
    
    form.fieldset(
        'configuration',
        label=_(u'Configuration'),
        fields=['start', 'stop', 'contact', 'logo'],
        )
    
    start = schema.Date(
        title=_(u'Project start'),
        description=_(u'Date project begins.'),
        required=False,
        )
    
    end = schema.Date(
        title=_(u'Project end'),
        description=_(u'Date project ends.'),
        required=False,
        )
    
    contacts = schema.List(
        title=_(u'Contact email'),
        description=_(u'Project contact email addresses, one per line.'),
        value_type=schema.BytesLine(),
        defaultFactory=list, #requires zope.schema >= 3.8.0
        )
    
    logo = NamedImage(
        title=_(u'Project logo'),
        description=_(u'Upload a project logo file as PNG or JPEG image.'),
        required=False,
        )


class ITeam(IWorkspace):
    """Marker for any kind of team (including sub-team) workspace"""
 

class ISubTeam(ITeam):
    """Marker for a specifically sub-team workspace"""


