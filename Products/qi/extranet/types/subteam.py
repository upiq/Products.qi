from zope.interface import implements

from Products.qi.extranet.types.interfaces import ISubTeam
from Products.qi.extranet.types.workspace import Workspace


class SubTeam(Workspace):
    """QI sub-team container"""

    implements(ISubTeam)

    portal_type = 'qisubteam'

