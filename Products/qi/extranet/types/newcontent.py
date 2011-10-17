from zope.interface import implements
from plone.dexterity.content import Container

from Products.qi.extranet.types.newinterfaces import IProject, ITeam, ISubTeam


class Workspace(Container):
    """Workspace base class"""
    
    implements(IWorkspace)


class Project(Workspace):
    """QI Project container"""
    
    implements(IProject)


class Team(Workspace):
    """QI team container"""
    
    implements(ITeam)


class ISubTeam(Workspace):
    """QI Sub-team container"""
    
    implements(ISubTeam)

