""" QITeamspace product interfaces.
"""

from OFS.interfaces import IOrderedContainer
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from zope import schema

from Products.qi import MessageFactory as _

from plone.app.vocabularies.users import UsersSource
from Products.qi.extranet.users.qiuser import QiUsersSource as UsersSource2

class IProject(ISelectableBrowserDefault, IOrderedContainer):
    """ QITeamspace project"""
    
    title = schema.TextLine(title=_(u"Title"),
                            description=_(u"Name of the project"),
                            required=True)
                            
    description = schema.Text(title=_(u"Description"),
                              description=_(u"A short summary of the project"),
                              required=True)
    
    hideinactiveteams = schema.Bool(title=_(u"Hide inactive teams?"),
                                    description=_(u"Keep inactive teams out of search results"),
                                    required=False)
    
    projectTheme =  schema.Choice(
        title=u"Theme",
        description=u"Project theme",
        default=u"Sunburst Theme",
        vocabulary="Products.qi.Skins",
        required=True)
    
    logo = schema.Bytes(title=_(u"Logo"),
                        description=_(u"Project logo"),
                        required=False)
 
IQIProject = IProject # b/c

class ITeam(ISelectableBrowserDefault, IOrderedContainer):
    """ QITeamspace Team"""
    
    title = schema.TextLine(title=_(u"Title"),
                            description=_(u"Name of the team"),
                            required=True)
                            
    description = schema.Text(title=_(u"Description"),
                              description=_(u"A short summary of the team"),
                              required=False)
    

IQITeam = ITeam

_PROJECT_LOGO_NAME = 'project_logo.jpg'


#from Products.qi.extranet.types.interfaces import ITeam

class ISubTeam(ITeam):
    #duplicates ITeam entirely
    pass

IQISubTeam = ISubTeam

