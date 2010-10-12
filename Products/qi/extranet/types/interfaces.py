""" QITeamspace product interfaces.
"""

from OFS.interfaces import IOrderedContainer
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from zope import schema

from Products.qi import MessageFactory as _

from plone.app.vocabularies.users import UsersSource
from Products.qi.extranet.users.qiuser import QiUsersSource as UsersSource2

class IProject(ISelectableBrowserDefault, IOrderedContainer):
    """ QITeamspace project
    """
    title = schema.TextLine(title=_(u"Title"),
                            description=_(u"Name of the project"),
                            required=True)
                            
    description = schema.Text(title=_(u"Description"),
                              description=_(u"A short summary of the project"),
                              required=True)

    hideinactiveteams = schema.Bool(title=_(u"Hide inactive teams?"),
									description=_(u"Keep inactive teams out of search results"),
									required=False)
    """
    managers = schema.List(title=_(u"Managers"),
                           description=_(
                           u"Search for and select a manager for this project"),
                           value_type=schema.Choice(title=_(u"User id"),
                                                   source=UsersSource2,),
                           required=False)
    
    faculty = schema.List(title=_(u"Faculty"),
                          description=_(
                          u"Search for and select faculty for this project"),
                          value_type=schema.Choice(title=_(u"User id"),
                                                   source=UsersSource,),
                          required=False)
                                                   
    addable_types = schema.Set(title=_(u"Addable types"),
                               description=_(
        u"These types will be addable by project members"),
                               value_type=schema.Choice(
                                       title=_(u"Type id"),
                                       vocabulary="Products.qi.AddableTypes")
                               )"""
                               
    projectTheme =  schema.Choice(
        title=u"Theme",
        description=u"Project theme",
        vocabulary="Products.qi.Skins",
        required=True)



    logo = schema.Bytes(title=_(u"Logo"),
                        description=_(u"Project logo"),
                        required=False)
 
IQIProject = IProject # b/c

class ITeam(ISelectableBrowserDefault, IOrderedContainer):
    """ QITeamspace Team
    """
    title = schema.TextLine(title=_(u"Title"),
                            description=_(u"Name of the team"),
                            required=True)
                            
    description = schema.Text(title=_(u"Description"),
                              description=_(u"A short summary of the team"),
                              required=False)
    
    """managers = schema.List(title=_(u"Leads"),
                           description=_(
        u"The following users should be leaders of this team"),
                           value_type=schema.Choice(title=_(u"User id"),
                                                   source=UsersSource,),
                           required=False)
                                                                              
    addable_types = schema.Set(title=_(u"Addable types"),
                               description=_(
        u"These types will be addable by team members"),
                               value_type=schema.Choice(
                                       title=_(u"Type id"),
                                       vocabulary="Products.qi.AddableTypes")
                               )
                               
    upload_types = schema.Set(title=_(u"Importable data types"),
                               description=_(
        u"these formats can be uploaded, when submitting data"),
                               value_type=schema.Choice(
                                       title=_(u"Upload id"),
                                       source='Products.qi.UploadableTypes')
                               )"""
IQITeam = ITeam

_PROJECT_LOGO_NAME = 'project_logo.jpg'


#from Products.qi.extranet.types.interfaces import ITeam

class ISubTeam(ITeam):
    #duplicates ITeam entirely
    pass
IQISubTeam = ISubTeam
