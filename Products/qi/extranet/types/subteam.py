from Products.qi.extranet.types.team import Team
from interfaces import ISubTeam, ITeam
from App.class_init import default__class_init__ as InitializeClass
from zope.component.factory import Factory
from zope.interface import implements
from Products.qi import MessageFactory as _
class SubTeam(Team):
    implements(ISubTeam)
    portal_type="qisubteam"
    def isSubTeam(self):
        return True

InitializeClass(SubTeam)
subTeamFactory = Factory(SubTeam, title=_(u"Create a new QI subteam"))
