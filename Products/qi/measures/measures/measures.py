from Products.Five.browser import BrowserView
import re
from qi.sqladmin import models as DB
from datetime import datetime
from datetime import date
from Products.qi.util.general import BrowserPlusView
from Products.qi.util import utils


def cmpMeasure(a,b):
    return cmp(a.shortname.lower(),b.shortname.lower())
        
def cmpMeasureType(a,b):
    return cmp(a.name.lower(),b.name.lower())
    
def cmpProjMeasures(a, b):
    result = cmp(a.measure.name.lower(), b.measure.name.lower())
    return result

    
def cmpProjTopics(a, b):
    result = cmp(a.topic.name.lower(), b.topic.name.lower())
    return result

class AddMeasureType(BrowserPlusView):
    processFormButtons=('create', 'delimg')
    
    def validate(self, form):
            
        if 'del' in form :
            mtypeid = form['del']
            isused = DB.Measure.objects.filter(measuretype=mtypeid)
            if isused.count() >= 1:
                message='Could not delete: That measure type is in use.'
                self.addError('delimg',message)
                return False
        else:
            self.requiredAvailable(DB.MeasureType.objects,'name')
    
    def existingTypes(self):
        return sorted(DB.MeasureType.objects.all().order_by("name"),cmpMeasureType)
    
    def action(self, form, action):
        if 'del' in form:
            delid=form['del'].strip()
            self.delMeasureType(delid)
        if 'name' in form :
            name=form['name']
            added=DB.MeasureType()
            added.name=name
            added.save()
            #self.doRedirect()
    
    def delMeasureType(self, mtypeid):
        mtype = DB.MeasureType.objects.get(id=mtypeid)
        mtype.delete()

class Measures(BrowserPlusView):
    
    processFormButtons=('add_measure','add_topic','apply-changes')
    nonValidatedButtons=('new',)
    
    def getPresentMeasures(self):
        dbproject=self.context.getDBProject()
        result=DB.ProjectMeasure.objects.filter(project=dbproject).order_by('measure')

        return utils.natsort(result, lambda arg: arg.measure.name and \
            arg.measure.name.lower() or arg.measure.shortname.lower())

        
    def getAvailableMeasures(self):
        ids=[k.measure.id for k in self.getPresentMeasures()]
        result=DB.Measure.objects.exclude(id__in=ids).order_by('shortname')
        return result
    
    def getPresentTopics(self):
        dbproject=self.context.getDBProject()
        result=DB.ProjectTopic.objects.filter(project=dbproject)
        return utils.natsort(result, lambda arg: arg.topic.name and \
            arg.topic.name.lower() or arg.topic.shortname.lower())
        
    
    def getAvailableTopics(self):
        ids=[k.topic.id for k in self.getPresentTopics()]
        return DB.Topic.objects.exclude(id__in=ids).order_by('name')
        
    def validate(self, form):
        if 'add_measure' in form:
            self.requiredInTable(self.getAvailableMeasures(),'measure')
            self.daterange('start','end',False, True)
            self.requiredValidation('validation')
            
        if 'add_topic' in form:
            self.requiredInTable(self.getAvailableTopics(),'topic')
            self.daterange('start','end',False, True)            
    def action(self,form, actionname):
    
        if actionname=='add_measure':
            measure=DB.Measure.objects.get(id=int(form['measure']))
            project=self.context.getDBProject()
            added=DB.ProjectMeasure()
            added.measure=measure
            added.project=project
            added.startdate=self.buildDate(form['start'])
            if form['end'].strip()!='':
                added.enddate=self.buildDate(form['end'])
            #if the measure is being added directly, we assume they want it on
            added.active=True
        
            added.validation=form['validation']
            added.reportFrequency='often'
            added.save()
        if actionname=='add_topic':
            project=self.context.getDBProject()
            topic=DB.Topic.objects.get(id=int(form['topic']))
            
            addedTopic=DB.ProjectTopic()
            addedTopic.topic=topic
            addedTopic.project=project
            addedTopic.startdate=self.buildDate(form['start'])
            addedTopic.enddate=self.buildDate(form['end'])
            addedTopic.active=True
            addedTopic.save()
            
            topicMeasures=DB.TopicMeasure.objects.filter(topic=topic)
            projectmeasures=DB.ProjectMeasure.objects.filter(project=project)
            for topicmeasure in topicMeasures:
                measureadded=topicmeasure.measure
                #if the project does not already have this measure
                if projectmeasures.filter(measure=measureadded).count()==0:
                    added=DB.ProjectMeasure() 
                    added.project=project
                    added.measure=measureadded
                    added.required=False
                    added.goal=topicmeasure.goal
                    added.active=True
                    added.validation=''
                    added.reportfrequency='rarely'
                    added.save() 
            
        if actionname=='new':
            self.doRedirect('Add_Measure.html')
        
        
        #if actionname=='activate' or actionname=='deactivate':
        #    topicids=[]
        #    if 'topics' in form:
        #        topicids=form['topics']
        #    measureids=[]
        #    if 'measures' in form:
        #        measureids=form['measures']
        #    topics=DB.ProjectTopic.objects.filter(id__in=topicids)
        #    measures=DB.ProjectMeasure.objects.filter(id__in=measureids)
        #
        #if actionname=='activate':
        #
        #    for topic in topics:
        #        topic.active=True
        #        topic.save()
        #    for measure in measures:
        #        measure.active=True
        #        measure.save()
        #        
        #if actionname=='deactivate':
        #    for topic in topics:
        #        topic.active=False
        #        topic.save()
        #    for measure in measures:
        #        measure.active=False
        #        measure.save()
        #
        
        if actionname=='apply-changes':
            topicRecords=[]
            if 'topics' in form:
                topicRecords=form['topics']
            measureRecords=[]
            if 'measureRecs' in form:
                measureRecords=form['measureRecs']
            for rec in measureRecords:
                projMeas=DB.ProjectMeasure.objects.get(id=rec.id)
                #projMeas.active=rec.active
                projMeas.startdate=self.buildDate(rec.startdate)
                projMeas.enddate=self.buildDate(rec.enddate)
                projMeas.save()      
                           
#now doubles as edit



class NewMeasure(BrowserPlusView):
    processFormButtons=('add',)
    
    def getExistingMeasures(self):
        return utils.natsort(DB.Measure.objects.all().order_by('name'), lambda arg: arg.name and \
            arg.name.lower() or arg.shortname.lower())
    
    def getMeasureTypes(self):
        return utils.natsort(DB.MeasureType.objects.all().order_by('name'), lambda arg: arg.name.lower())
    
    def validate(self, form):
        self.required('name')
        measureid=-1
        if self.requiredInForm('measureid'):
            measureid=int(form['measureid'])
        if measureid>0:
            self.required('shortname')
        else:
            self.requiredAvailable(DB.Measure.objects,'shortname','shortname',
                'Short Name')
        #no duplicate short names
        
        #these are merely only required to exist, not have a value
        self.requiredInForm('definition')
        self.requiredInForm('guidance')
        self.requiredInForm('source')
        self.requiredInForm('type')
        self.requiredValidation('validation')
        self.requiredInForm('goal')
        self.requiredInForm('userdefined')
        
        
        if self.requiredInForm('version'):
            if form['version']!='':
                self.requiredVersionNumber('version')
        #required in table REALLY means required in queryset
        self.requiredInTable(DB.MeasureType.objects,'measuretype')
    
    def action(self, form, actionname):
        if actionname=='add':
            measureid=int(form['measureid'])
            if measureid<0:
                added=DB.Measure()
            else:
                added=DB.Measure.objects.get(id=measureid)
            added.name=form['name']
            added.shortname=form['shortname']
            added.definition=form['definition']
            added.guidance=form['guidance']
            added.source=form['source']
            added.ttype=form['type']
            added.validation=form['validation']
            added.goal=form['goal']
            added.userdefined=form['userdefined']
            added.versionnumber=form['version']
            added.measuretype=DB.MeasureType.objects.get( \
                id=int(form['measuretype']))
                
            added.save()
            self.doRedirect('Add_Measure.html')
    
    def generalUpdate(self):
        request=self.request
        if request.has_key('measureid') and int(request['measureid'])>0:
            #lazy verification that they didn't submit a form
            if not request.has_key('shortname'):
                measure=DB.Measure.objects.get(id=int(request['measureid']))
                request['name']=measure.name
                request['shortname']=measure.shortname
                request['definition']=measure.definition
                request['guidance']=measure.guidance
                request['source']=measure.source
                request['type']=measure.ttype
                request['validation']=measure.validation
                request['goal']=measure.goal
                request['userdefined']=measure.userdefined
                request['version']=measure.versionnumber
                request['measuretype']=measure.measuretype.id
            
            
    