from Products.CMFCore.utils import getToolByName

from psycopg2 import IntegrityError 
from Acquisition import aq_base, aq_inner, aq_parent

#from django.contrib.auth.models import User 
from qi.sqladmin import models 
from datetime import datetime
from Products.qi.extranet.types.interfaces import ITeam
from zope.app.container.contained import ObjectAddedEvent
from Products.qi.util.logger import logger

from qi.sqladmin import models as DB

def persistProjectToDjango(project, event):
    """Give the given role the add permission on all the selected types.
    """
    try:
        if not project.dbid:
            dbproj=freshProject()
        else:
            try:
                dbproj=models.Project.objects.get(id__exact=project.dbid)
            except models.Project.DoesNotExist:
                dbproj=freshProject()
    except AttributeError:
        dbproj=freshProject()
    
    dbproj.name=project.title
    dbproj.description=project.description
    dbproj.hideinactiveteams=project.hideinactiveteams
    try:  
        dbproj.save()
    except Exception, e:
        logger.handleException(e)
    #keep updated on our pointers
    project.dbid=dbproj.id

def freshProject():
    dbproj=models.Project()
    return dbproj
    

def persistTeamToDjango(team, event):
    name=team.title
    if isinstance(event,ObjectAddedEvent):
        project,parent=findDbProjectTeamEvent(event)
    else:
        project,parent=findDbProjectTeam(team)
    try:
        if not team.dbid:
            existing=project.team_set.filter(name=name)
            if len(existing)>0:
                raise KeyError("Creating a duplicate team name")
                #existing.delete()
            dbteam=freshTeam()
        else:
            try:
                dbteam=models.Team.objects.get(id__exact=team.dbid)
            except models.Team.DoesNotExist:
                dbteam=freshTeam()
    except AttributeError:
        existing=project.team_set.filter(name=name)
        if len(existing)>0:
            existing.delete()
        dbteam=freshTeam()
    #isinstance used here because we have no control over these interfaces    
    dbteam.project=project
    dbteam.parent=parent
    dbteam.name=team.title
    dbteam.description=team.description or  'NO DESCRIPTION PROVIDED'
    dbteam.active=True
    logger.logText('attempting to save soon')
    try:
        logger.logText('saving a team %s'%team.title)
        dbteam.save()
        logger.logText('saved a team')
    except Exception, e:
        logger.logText('Exception occurred')
        logger.handleException(e)
    team.dbid=dbteam.id
    
def freshTeam():
    dbteam=models.Team()
    return dbteam

def removePloneFromDjango(ploneitem, event):
    if not ploneitem.dbid:
        #done already!
        return
        
    if isinstance(ploneitem, ITeam):
        table=models.Team.objects
    else:
        table=models.Project.objects
    try:
        dbteam=table.get(id__exact=ploneitem.dbid)
    except models.Team.DoesNotExist:
        #oh, done again, already?????
        return
    except models.Project.DoesNotExist:
        return
    #there is likely an unhandled exception here of some stripe,
    #but for now this is 'safe enough'
    return #no don't do this
    dbteam.delete()

def findDbProjectTeamEvent(event):
    project=event.newParent.getDBProject() 
    try:
        team=event.newParent.getDBTeam()
    except AttributeError:
        team=None
    return project, team
    """
    project=event.newParent.getProject()
    team=event.newParent.getTeam()
    try:
        if not project.dbid:
            persistProjectToDjango(project, None)
    except AttributeError:
        persistProjectToDjango(project,None)
    try:
        dbproj=models.Project.objects.get(id=project.dbid)
    except models.Project.DoesNotExist:
        persistProjectToDjango(project,None)
        dbproj=models.Project.objects.get(id=project.dbid)

    return dbproj,team.getDBTeam()"""

def findDbProjectTeam(team):
    
    parent=aq_parent(aq_inner(team))
    project=parent.getDBProject() 
    try:
        team=parent.getDBTeam()
    except AttributeError:
        team=None
    return project, team

    """if not project.dbid:
        persistProjectToDjango(project, None)
    try:
        dbproj=models.Project.objects.get(id=project.dbid)
    except models.Project.DoesNotExist:
        persistProjectToDjango(project,None)
        dbproj=models.Project.objects.get(id=project.dbid)
    return dbproj"""
"""
def addUserToDjango(event):
    principal = event.principal
    user = User()
    user.username = principal.getUserName()[:30]
    user.is_staff = True
    try:
        user.save()
    except IntegrityError, e:
        e.cursor.connection.rollback()
        #print 'database problem:duplicate user'
        pass
    """
def removeUserFromDjango(event):
    # XXX this is not yet called because PAS doesn't ever actually
    # send an IPrincipalDeletedEvent (even though it defines one) :-(
    principal = event.principal
    username = principal.getUserName()
    try:
        django_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return
    django_user.delete()