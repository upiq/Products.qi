from Products.qi.util import utils
from qi.sqladmin import models as DB

def findAbandonedDBTeams(context):
    pteams=utils.getTeamsInContext(context)
    dbids=[t.dbid for t in pteams if hasattr(t, 'dbid')]
    dbteams=DB.Team.objects.all().exclude(id__in=dbids)
    return dbteams

def findAbandonedDBProjects(context):
    pprojects=utils.getProjectsInContext(context)
    dbids=[t.dbid for t in pprojects if hasattr(t, 'dbid')]
    dbprojs=DB.Project.objects.all().exclude(id__in=dbids)
    return dbprojs