from plone.app.form import base
from zope.formlib import form
from Products.qi.report.internal.model.interfaces import IQIChart
from zope.component import createObject
from operator import itemgetter
from Products.qi.util.general import BrowserPlusView

from qi.sqladmin import models as DB

#use message factory like this to make a constant message
from Products.qi import MessageFactory as _

chart_form_fields = form.Fields(IQIChart)
class AddForm(base.AddForm):
    
    form_fields = chart_form_fields
    label = _(u"Add Chart")
    form_name = _(u"Chart Settings")

    def setUpWidgets(self, ignore_request=False):

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)

    def create(self, data):
        chart = createObject(u"qi.Chart")
        form.applyChanges(chart, self.form_fields, data)
        return chart

class EditForm(base.EditForm):
    form_fields = chart_form_fields
    label = _(u"Edit Chart")
    form_name = _(u"Modify Chart Parameters")
    
aggs=('min','max','avg')

class View(BrowserPlusView):
    removeBorders=False
    processFormButtons= ('submitorder',)
    
    def action(self, form, action):
        self.getOrder(self.context.measures._data.keys(), form, 'measure')
        self.getOrder(self.context.derived._data.keys(), form, 'derived')

    def validate(self, form):
        pass

    def measures(self):
        if hasattr(self.context, 'orderlist'):
            out = []
            for m in self.context.orderlist['measure']:
                out.insert(self.context.orderlist['measure'].index(m), DB.Measure.objects.get(id=m))
            return out
        else:
            return DB.Measure.objects.filter(id__in=self.context.measures._data.keys())
            
    def measureids(self):
        if not hasattr(self.context, 'orderlist'):
            return self.context.measures._data.keys()
        else:
            return self.context.orderlist['measure']
    def titlefor(self, x):
        return DB.Measure.objects.get(id=int(x)).name
    def computedtitlefor(self, x):
        return DB.Percentage.objects.get(id=int(x))
        
    def getVars(self, measure):
        teams=["'%s'"%str(x) for x in self.context.teams._data.keys()]
        measures=self.context.measures._data.keys()
        result="""
        var teamids=[%s];
        var measureid=%i;
        basepath="%s/amline/";"""
        return result%(','.join(teams),measure,self.context.absolute_url())
        
    def computedMeasures(self):
        if hasattr(self.context, 'derived'):
            if hasattr(self.context, 'orderlist'):
                out = []
                for m in self.context.orderlist['derived']:
                    out.insert(self.context.orderlist['derived'].index(m), DB.Measure.objects.get(id=m))
                return out
            else: 
                return DB.Percentage.objects.filter(id__in=self.context.derived._data.keys())
        else:
            return []
        
    def computedids(self):
        if not hasattr(self.context, 'derived'):
            return []
        else:
            if hasattr(self.context, 'orderlist'):
                return self.context.orderlist['derived']
            else:
                return self.context.derived._data.keys()
                
    
    def missingany(self):
        for x in self.measureids():
            if not self.hasData(int(x)):
                return True
        return False
    
    def hasData(self, measureid):
        teamids=self.context.teams._data.keys()
        searchedids=[]
        for x in teamids:
            if isinstance(x,str) and (x.startswith('min') or x.startswith('max') or x.startswith('avg')):
                addedids=[team.id for team in self.context.getDBProject().team_set.all()]
            else:
                addedids=[x]
            searchedids.extend(addedids)
        count= DB.MeasurementValue.objects. \
            filter(measure__id=measureid). \
            filter(team__in=searchedids). \
            count()
        return count>0
            
    def getOrder(self, measures, form, mod):
        
        if hasattr(self.context, 'orderlist'):
            if not hasattr(self.context.orderlist, mod):
                self.context.orderlist[mod] = []

            o = self.context.orderlist[mod]
        else:
            self.context.orderlist = dict()
            o = []
            
        suborder = sorted(form.items(), key=itemgetter(1))
        
        for mid in suborder:
            if mid[0] != 'submitorder' and int(mid[0]) in measures and self.hasData(int(mid[0])):
                o.insert(int(mid[1]), int(mid[0]))
                               
        for m in measures:
            if m not in o:
                o.append(m)
                
        seen = set()
        o = [x for x in o if x not in seen and not seen.add(x)]

        self.context.orderlist[mod] = o
        self.context.orderlist_p_changed = True
        return self.context.orderlist[mod]

    