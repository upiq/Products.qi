from zope.interface import implements

from Products.qi.extranet.types.interfaces import IProject
from Products.qi.extranet.types.workspace import Workspace


class Project(Workspace):
    """QI project container"""
    
    implements(IProject)
    
    portal_type = 'qiproject'

