import os
import re

from zope import dottedname
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName 
from Products.CMFPlone.interfaces import IPloneSiteRoot

from qi.sqladmin import models as DB
from Products.qi.util.logger import logger
from Products.qi.extranet.types import project, team
from Products.qi.util.config import PathConfig


def find_parents(context, typename=None, findone=False, start_depth=2):
    if findone and typename is None:
        parent = getattr(context, '__parent__', None)
        if parent:
            return parent #immediate parent of context
    result = []
    catalog = getToolByName(context, 'portal_catalog')
    path = context.getPhysicalPath()
    for subpath in [path[0:i] for i in range(len(path)+1)][start_depth:]:
        query = {
            'path' : { 
                'query' : '/'.join(subpath),
                'depth' : 0,
                },
            'Type' : typename,
            }
        if typename is None:
            del(query['Type'])
        brains = catalog.search(query)
        if not brains:
            continue
        else:
            item = brains[0]._unrestrictedGetObject()
            if findone:
                return item
            result.append(item)
    if findone:
        return None # never found one
    return result


def find_parent(context, typename=None, start_depth=2):
    return find_parents(context, typename, findone=True, start_depth=start_depth)


def project_containing(context):
    return find_parent(context, typename='QI Project')


def team_containing(context):
    return find_parent(context, typename='QI Team', start_depth=3)


def getProjectsInContext(context):
    catalog = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath())
    query = {
        'path' : {
            'query' : path,
            'depth' : 2
            },
        'Type' : 'QI Project',
        }
    return [b._unrestrictedGetObject() for b in catalog.search(query)]


def getTeamsInContext(context):
    catalog = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath())
    query = {
        'path' : {
            'query' : path,
            'depth' : 2
            },
        'Type' : 'QI Team',
        }
    return [b._unrestrictedGetObject() for b in catalog.search(query)]


def getPloneProject(dbproject, context):
    if dbproject is None:
        return None
    projects=getProjectsInContext(getSite())
    for project in projects:
        if project.dbid==dbproject.id:
            return project


def getPloneTeam(dbteam, context):
    if dbteam is None:
        return None
    teams=getTeamsInContext(getSite())
    for team in teams:
        if team.dbid==dbteam.id:
            return team 


def getTeamGroups(project,dblist):
    plonegroups=[]
    teams=getTeamsInContext(project)
    subscribedteams=[team.id for team in dblist.teams.all()]
    for kteam in teams:
        if kteam.dbid in subscribedteams:
            plonegroups.append(kteam.getGroup())
    return plonegroups
    

def getAllPloneGroups(dblist,project, team, context):
    plonegroups=[]
    groups=dblist.groups.all()
    for group in groups:
        addgroups(
            plonegroups,
            getPloneGroupNames(
                group.groupname,
                project,
                team,
                context))
    return plonegroups
    
    
def addgroups(plonegroups, groups):
    plonegroups[len(plonegroups):]=groups
    

def getPloneGroupNames(group, project, team, context):
    result=[]
    if project is None:
        if group=='managers':
            site=getSite()
            allprojects=getProjectsInContext(site)
            for eachproject in allprojects:
                result.appendeachproject.getProjectGroup('managers')
            return result
            
    if project is not None and team is None:
        if group=='leads':
            allteams=getTeamsInContext(project)
            for eachteam in allteams:
                result.append(eachteam.getGroup('leads'))
            return result
        else:
            return [project.getProjectGroup(group),]
    if project is not None and team is not None:
        target='%s-%s-%s'%(project.getId(),team.getId(),group)    
        return [target,]


def getProjectsAndTeamsForUser(user, context):
    teams=[]
    projects=[]
    
    site=getSite()
    allprojects=getProjectsInContext(site)
    allteams=getTeamsInContext(site)
    for project in allprojects:
        for projuser in project.getProjectUsers():
            if projuser==str(user):
                projects.append(project)
    for team in allteams:
        for teamuser in team.getTeamUsers():
            if teamuser==str(user):
                teams.append(team)
    return projects,teams



#this is only for the natsort function below    
def convert(text):
    if text.isdigit():
        return int(text)
    else:
        return text


def natsort(tosort, f=lambda arg: arg.lower()):
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', f(key)) ] 
    return sorted(tosort, key=alphanum_key )

    
def namedquery(name, **kwargs):
    name = 'Products.qi.util.queries.%s' % name
    sql_template = dottedname.resolve.resolve(name)
    from django.db import connection, transaction
    cursor=connection.cursor()
    try:
        cursor.execute(querytext % kwargs)
        return [x[:] for x in cursor]
    except Exception, e:
        import sys, traceback
        x,y,trace=sys.exc_info()
        print x, y
        traceback.print_tb(trace)
        connection._rollback()
        raise
    cursor.close()

