""" QITeamspace product interfaces.
"""

from OFS.interfaces import IOrderedContainer
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from zope import schema

from Products.qi import MessageFactory as _


_PROJECT_LOGO_NAME = 'project_logo.jpg'


class IProject(ISelectableBrowserDefault, IOrderedContainer):
    """ QITeamspace project"""
    
    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Name of the project"),
        required=True,
        )
                            
    description = schema.Text(
        title=_(u"Description"),
        description=_(u"A short summary of the project"),
        required=False,
        )
    
    logo = schema.Bytes(
        title=_(u"Logo"),
        description=_(u"Project logo"),
        required=False,
        )

 
class ITeam(ISelectableBrowserDefault, IOrderedContainer):
    """ QITeamspace Team"""
    
    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Name of the team"),
        required=True,
        )
    
    description = schema.Text(
        title=_(u"Description"),
        description=_(u"A short summary of the team"),
        required=False,
        )


class ISubTeam(ITeam):
    """marker for sub-team"""

