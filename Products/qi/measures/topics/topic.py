from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB

class TopicList(BrowserPlusView):
    processFormButtons=('add',)
    def validate(self,form):
        self.requiredAvailable(DB.Topic.objects,'name','name','Topic Name')
    
    def action(self, form, action):
        if action=='add':
            added=DB.Topic()
            added.name=form['name']
            added.save()
    
    def getTopics(self):
        return DB.Topic.objects.all()
    
    #expected behavior: re
    def getMeasures(self, topic):
        return DB.TopicMeasure.objects.filter(topic=topic)
        
class EditTopic(BrowserPlusView):
                    
    processFormButtons=('add',)
    nonValidatedButtons=('new',)
    def validate(self,form):
        self.requiredInTable(DB.Topic.objects,'topicid','Topic ID')
        self.requiredInTable(DB.Measure.objects,'measure')
        self.requiredDate('start')
        self.optionalDate('end')
        self.requiredInForm('goal')
        
    def action(self, form, action):
        print 'action %s'%action
        if action=='add':
            topic=DB.Topic.objects.get(id=int(form['topicid']))
            measure=DB.Measure.objects.get(id=int(form['measure']))
            added=DB.TopicMeasure()
            added.topic=topic
            added.measure=measure
            added.startdate=self.buildDate(form['start'])
            if form['end'].strip()!='':
                added.enddate=self.buildDate(form['end'])
            added.goal=form['goal']
            added.active=False
            added.save()
            self.request['topicid']=form['topicid']
        if action=='new':
            self.doRedirect('Add_Measure.html')
    
    def availableMeasures(self):
        usedTopicMeasures=DB.TopicMeasure.objects.filter(topic=self.topic())
        usedMeasures=[k.measure.id for k in usedTopicMeasures]
        return DB.Measure.objects.exclude(id__in=usedMeasures)
    
    def measures(self):
        return DB.TopicMeasure.objects.filter(topic=self.topic()). \
            select_related()
    
    def topic(self):
        return DB.Topic.objects.get(id=self.topicid)
    def generalUpdate(self):
        self.topicid=self.request['topicid']
        
    