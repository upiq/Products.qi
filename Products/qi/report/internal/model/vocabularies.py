from zope.interface import implementer

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from Products.qi.util.utils import natsort
from qi.sqladmin import models as DB

from Products.CMFCore.utils import getToolByName

@implementer(IVocabularyFactory)
def Teams(context):
    project=context.getDBProject()
    if hasattr(context,'getDBTeam'):
        dbteam=context.getDBTeam()
        teams=DB.Team.objects.filter(id=dbteam.id) | dbteam.team_set.all().order_by('name')
    else:
        teams=project.team_set.all()
    #Get parent teams first because they may have active children even if they aren't active themselves
    parentteams=getParentTeams(teams)
    if project.hideinactiveteams: teams=teams.filter(active=True) 
    name=project.name
    items=[(x.name,x.id) for x in teams]
    items=natsort(items, lambda (x,y): x.lower())
    for team in parentteams:
        items.insert(0,('%s Maximum'%team.name,'max-%i'%team.id))
        items.insert(0,('%s Average'%team.name,'avg-%i'%team.id))
        items.insert(0,('%s Minimum'%team.name,'min-%i'%team.id))
    items.insert(0,('%s Maximum'%name,'max'))
    items.insert(0,('%s Average'%name, 'avg'))
    items.insert(0,('%s Minimum'%name,'min'))
    return SimpleVocabulary.fromItems(items)
    
def getParentTeams(teams):
    result=[]
    for x in teams:
        if x.team_set.all().count()>0:
            result.append(x)
    if len(teams)==1 and teams[0].parent is not None:
        result.append(teams[0].parent)
    return result

def sortmeasure(x,y):
    return cmp(x[0].lower(),y[0].lower())
    
@implementer(IVocabularyFactory)
def Measures(context):
    dbproj=context.getDBProject()
    projmeasures=dbproj.projectmeasure_set.all()
    #allmeasures=DB.Measure.objects.all()
    return SimpleVocabulary.fromItems(sorted([(x.measure.name or x.measure.shortname,x.measure.id) for x in projmeasures],sortmeasure))

@implementer(IVocabularyFactory)
def DerivedMeasures(context):
    allderivedvalues=DB.Percentage.objects.filter(project=context.getDBProject()).order_by('name')
    return SimpleVocabulary.fromItems([(x.name,x.id) for x in allderivedvalues])
    
def ChartDates(context):
    project=context.getDBProject()
    dates=project.datadate_set.filter(form__isnull=True)
    return SimpleVocabulary.fromItems([(x.name, x.period) for x in dates])