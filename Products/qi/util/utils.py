import os
import re

from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName 
from Products.CMFPlone.interfaces import IPloneSiteRoot

from qi.sqladmin import models as DB
from general import BrowserPlusView
from Products.qi.util.logger import logger
from Products.qi.extranet.types import project, team
from Products.qi.util.config import PathConfig

SQLPATH = PathConfig().get('sql', 'src/sql') 


def getProjectParent(context):
    path = context.getPhysicalPath()
    portal = getSite()
    all_projects = getProjectsInContext(portal)
    for project in all_projects:
        project_path = project.getPhysicalPath()
        if project_path == path[:len(project_path)]:
            return project


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
    

def getUsersForMailingList(dblist, context):
    userids={}
    if not dblist:
        return ()
        
    project=getPloneProject(dblist.project, context)
    team=getPloneTeam(dblist.team, context)
    individualUsers=dblist.mailinglistsubscriber_set.all()

    for user in individualUsers:
        userids[user.userid]=user.userid

    plonegroups=[]

    #if it's a project, append team groups
    if project and not team:
        addgroups(plonegroups,getTeamGroups(project,dblist))
    
    addgroups(plonegroups,getAllPloneGroups(dblist,project,team,context))
    
    userplugin=context.acl_users.source_groups
    for plonegroup in plonegroups:
        for user in userplugin.listAssignedPrincipals(plonegroup):
            userids[user[0]]=user[0]
    
    result= [k for k in userids.iterkeys()]
    return result
    
        
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


def getPossibleListsForUser(user, context):
    projects, teams=getProjectsAndTeamsForUser(user, context)
    base=DB.MailingList.objects
    lists=base.filter(project__isnull=True,team__isnull=True)
    for project in projects:
        dbproj=project.getDBProject()
        lists=lists | base.filter(project=dbproj,team__isnull=True)
    for team in teams:
        dbteam=team.getDBTeam()
        dbproj=team.getDBProject()
        lists=lists | base.filter(project=dbproj, team=dbteam)
    return lists


def getListsForUser(user, context):
    userobj=context.acl_users.getUser(user)
    if userobj is None:
        logger.logText('invalid user detected, giving no lists: %s'%user)
        return []
    catalog=context.portal_catalog
    grouptool=context.acl_users.source_groups
    groups=userobj.getGroupIds()
    alllists=[]
    lists=DB.MailingList.objects.filter(mailinglistsubscriber__userid=user)
    alllists.extend(lists)
    #projectbrains=[]
    #teambrains=[]
    for x in groups:
        try:
            mainpart, trimmed=x.rsplit('-',1)
            if trimmed=='lead':
                trimmed='leads'
        except ValueError:
            continue
        try:
            specialgroup=DB.SpecialMailGroup.objects.get(groupname=trimmed)
        except DB.SpecialMailGroup.DoesNotExist:
            continue
        members='%s-members'%mainpart
        projects=catalog.searchResults(meta_type='qiproject',getProjectGroup=members)
        for x in projects:
            dblists=DB.MailingList.objects.filter(project__id=x.dbid, team__id__isnull=True,groups=specialgroup)
            alllists.extend(dblists)
        
        teams=[]
        teams.extend(catalog.searchResults(meta_type="qiteam",getGroup=members))
        teams.extend(catalog.searchResults(meta_type="qisubteam",getGroup=members))
        for x in teams:
            dblists=DB.MailingList.objects.filter(team__id=x.dbid, groups=specialgroup)
            alllists.extend(dblists)
            if trimmed=="members":
                dblists=DB.MailingList.objects.filter(teams=x.dbid)
                alllists.extend(dblists)
        allids=[o.id for o in alllists]
        return DB.MailingList.objects.filter(id__in=allids)
    

#this is only for the natsort function below    
def convert(text):
    if text.isdigit():
        return int(text)
    else:
        return text


def natsort(tosort, f=lambda arg: arg.lower()):
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', f(key)) ] 
    return sorted(tosort, key=alphanum_key )

    
def compareMailingLists(leftList, rightList):
    return cmp(leftList.listname,rightList.listname)

    
def compareMailingLists2(left, right):
    return cmp(left.listname.lower(), right.listname.lower())


class fixUsers(BrowserPlusView):
    def __call__(self, *args, **kw):
        return fixTheUsers(self.context)


def fixTheUsers(site):
    pm = site.portal_membership
    members = pm.listMemberIds()

    out = []
    for member in members:
        # now get the actual member
        m = pm.getMemberById(member)
        # get the editor property for that member
        p = m.getProperty('wysiwyg_editor', None)

        out.append("%s %s" % (p, member))
        if p is not None and p != 'Epoz':
            m.setMemberProperties({'wysiwyg_editor': 'FCKeditor',})
            out.append("Changed property for %s" % member)
    return "\n".join(out)


"""
from Products.qi.util.utils import testquery
testquery("ProjAggChartLine",project_id=1, percentage_id=1, func='max')
testquery("formdates", project_id=31, form_id=13)
"""
def testquery(query, **kw):
    queryfile = open(os.path.join(SQLPATH, 'paramqueries/%s.sql' % query))
    querytext=queryfile.read()
    from django.db import connection, transaction
    

    cursor=connection.cursor()
    try:
        cursor.execute(querytext%kw)
        result= [x[:] for x in cursor]
    except Exception, e:
        import sys
        import traceback
        x,y,trace=sys.exc_info()
        print x, y
        traceback.print_tb(trace)
        
        #print trace
        connection._rollback()
        raise
        
    cursor.close()
    return result

