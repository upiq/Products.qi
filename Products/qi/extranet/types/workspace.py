from zope.interface import implements
from plone.dexterity.content import Container

from Products.qi.extranet.types.interfaces import IWorkspace


class Workspace(Container):
    """Workspace base class"""

    implements(IWorkspace)

