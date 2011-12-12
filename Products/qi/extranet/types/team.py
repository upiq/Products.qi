from zope.interface import implements

from Products.qi.extranet.types.interfaces import ITeam
from Products.qi.extranet.types.workspace import Workspace


class Team(Workspace):
    """QI team container"""
    
    implements(ITeam)

