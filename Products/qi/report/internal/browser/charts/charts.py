from Products.Five.browser import BrowserView
#from Products.qi.charts.piechart import PieChart
from PIL import Image
from StringIO import StringIO
from Products.qi.util.logger import logger
from qi.sqladmin import models as DB
#from Products.qi.charts.datamodel import Column
from Products.qi.util.general import BrowserPlusView
from datetime import date
from threading import Semaphore
import gc

class DummyValue(object):
    value=None
    perseverated=False
    
#overloadBlocker=Semaphore(8)

class ChartPage(BrowserPlusView):
    chartsize=('200','200')
    foundteams=None
    def __call__(self, *args, **kw):
        self.dates=None
        try:
            try:
                #overloadBlocker.acquire()
                self.update(*args, **kw)
                return self.index(*args,**kw)
            except Exception, e:
                logger.handleException(e, self)
                self.doRedirect('Error.html')
        finally:
            pass
            #overloadBlocker.release()
            #expensive but necessary
            #gc.collect()
    def getChartUrl(self):
        basestring="http://chart.apis.google.com/chart?%s"
        return basestring%('&'.join(self.params()))
    def params(self):
        params=self.getAllParams()
        return ['='.join(p) for p in params]
    def getAllParams(self):
        return  (
                ('cht','lc'),
                ('chs','x'.join(self.chartsize)),
                ('chxt','x'),
                ('chxl','0:=%s'%('|'.join(self.Periods()))),
                ('chd','t:%s'%(','.join(self.Data()))),
                )
    def teamids(self):
        if self.foundteams:
            return self.foundteams
        result=[]
        for x in self.request.form['teamid'].split('|'):
            try:
                added=int(x)
            except ValueError:
                added=x
            result.append(added)
        self.foundteams=result
        return result
            
    def goal(self):
        try:
            if 'measureid' in self.request.form:
                result = float(DB.Measure.objects.get(id=int(self.request.form['measureid'])).goal)
            else:
                result = float(DB.Percentage.objects.get(id=int(self.request.form['derivedid'])).goal)
            return result
        except Exception, e:
            return None
    def Set(self, teamid):
        form=self.request.form
        measureid=int(form['measureid'])
        #teamid=int(form['teamid'])
        measure=DB.Measure.objects.get(id=measureid)
        if teamid in ('min','max','avg'):
            teams=self.context.getDBProject().team_set.all()
            dataset=DB.MeasurementValue.objects.filter(measure=measure, team__in=teams, series__isnull=True).order_by('itemdate')
        elif isinstance(teamid, str) and ( teamid.startswith('min-') or teamid.startswith('max-') or teamid.startswith('avg-')):
            parentobj=DB.Team.objects.get(id=int(teamid[4:]))
            teams=parentobj.team_set.all()
            dataset=DB.MeasurementValue.objects.filter(measure=measure, team__in=teams, series__isnull=True).order_by('itemdate')
        else:
            team=DB.Team.objects.get(id=teamid)
            dataset=DB.MeasurementValue.objects.filter(measure=measure, team=team, series__isnull=True).order_by('itemdate')


        return dataset
    
    def includesdate(self, date):
        if self.context.startdate and date<self.context.startdate:
            return False
        if self.context.enddate and date>self.context.enddate:
            return False
        return True
    
    def Periods(self):
        #teamids=self.teamids()
        
        form=self.request.form
        if 'measureid' in form:
            self.LoadNonPercentageValues()
            return sorted([x for x in self.dates.keys() if self.includesdate(x)])
            measureid=int(form['measureid'])
            measure=DB.Measure.objects.get(id=measureid)
            dataset=DB.MeasurementValue.objects.filter(measure=measure)
            if 'min' in teamids or 'max' in teamids or 'avg' in teamids:
                actualids=[x.id for x in self.context.getDBProject().team_set.all()]
                dataset=dataset.filter(team__id__in=actualids)
            else:
                superteams=[]
                otherteams=[]
                for x in teamids:
                    if isinstance(x, str) and (x.startswith('min-') or x.startswith('max-') or x.startswith('avg-')):
                        superteams.append(int(x[4:]))
                    else:
                        otherteams.append(int(x))
                dataset=dataset.filter(team__id__in=otherteams) | dataset.filter(team__parent__id__in=superteams)
            filtered=dataset.extra(where=["value ~ '^[0-9]+(?:\.[0-9]+)?$'"])
            dates=sorted(list(set([x.itemdate for x in dataset])))
            return ['%s/%s/%s'%(date.month,date.day, date.year) for date in dates]
        else:
            self.LoadAllPercentageValues()
            return sorted([x for x in self.dates.keys() if self.includesdate(x)])
            #derivedid=int(form['derivedid'])
            #derived=DB.DerivedMeasureValue.objects.get(id=derivedid)
            #return ['%s/%s/%s'%(x.month,x.day, x.year) for x in derived.dates(self.teamids())]

    def LoadNonPercentageValues(self):
        form=self.request.form
        if self.dates is not None:
            return
        measure=DB.Measure.objects.get(id=int(form['measureid']))
        self.dates={}
        for team in self.teamids():
            if team in ('min','max','avg'):
                records=measure.getValues(aggregate=team, project_id=self.context.getDBProject().id)
            elif isinstance(team, str):
                records=measure.getValues(team_id=int(team[4:]),aggregate=team[:3])
            else:
                records=measure.getValues(team_id=team)
            for month, note,value  in records:
                teamvalues=self.dates.get(month,{})
                teamvalues[team]=(value, note)
                self.dates[month]=teamvalues
    
    def LoadAllPercentageValues(self):
        form=self.request.form
        if self.dates is not None:
            return
        percentage=DB.Percentage.objects.get(id=int(form['derivedid']))
        self.dates={}
        for team in self.teamids():
            if team in ('min','max','avg'):
                records=percentage.getValues(aggregate=team)
            elif isinstance(team, str):
                records=percentage.getValues(team_id=int(team[4:]),aggregate=team[:3])
            else:
                records=percentage.getValues(team_id=team)
            for month, note,value  in records:
                teamvalues=self.dates.get(month,{})
                teamvalues[team]=(value, note)
                self.dates[month]=teamvalues
                
    def period(self, x):
        return '%s/%s'%(x.itemdate.month,x.itemdate.year)
    def Data(self,teamid):
        return [(str(x.value),self.period(x)) for x in self.Set(teamid)]
    def getColor(self, measurevalue):
        annotation=getattr(measurevalue, 'description','')
        if not annotation:
            return ""
        try:
            int(annotation)
            return ""
        except:
            return "#FF0000"
    def valueFor(self, period, team):
        form=self.request.form
        if 'measureid' in form:
            result=DummyValue()
            found=self.dates.get(period,{}).get(team, None)
            if not found:
                return None
            result.value, result.description=found
            return result

        else:
            result=DummyValue()
            found=self.dates.get(period,{}).get(team, None)
            if not found:
                return None
            result.value, result.description=found
            return result
            
    def getDerived(self):
        if hasattr(self, 'derived'):
            return self.derived
        derivedid=int(self.request.form['derivedid'])
        derived=DB.Percentage.objects.get(id=derivedid)
        self.derived=derived
        return self.derived
    def findnames(self, searched):
        result=[]
        if searched.find('{')>-1:
            ignored,rest=searched.split('{',1)
            name, searchedagain=rest.split('}',1)
            result.append(DB.Measure.objects.get(shortname=name))
            result.extend(self.findnames(searchedagain))
        return result

class ChartData(ChartPage):
    def tagFor(self, tfile):
        if tfile is not None:
            url='%s/status?fileid=%i'%(self.context.absolute_url(),tfile.id)
            return "<a href='%s'>%s</a>"%(url,tfile.displayname)
        return "Data Entry"

class DummyTeam:
    pass

class ChartSettings(BrowserPlusView):
    
    def Teams(self):
        teams=[]
        for x in self.request.form['teamid'].split('|'):
            try:
                idval=int(x)
                team=DB.Team.objects.get(id=idval)
            except ValueError:
                team=DummyTeam()
                team.id=x
                #print self.context.teams
                #team.name=self.context.teams._data.get(x,'Unknown team')
                team.name={'min':'Minimum','max':'Maximum','avg':'Average'}.get(x[:3],'Unknown')
                if len(x)>3:
                    #I know string concatenation sucks, but formatting for just a space seemed silly
                    team.name=DB.Team.objects.get(id=int(x[4:])).name+" "+team.name
            teams.append(team)
        return teams
    def Measure(self):
        if 'measureid' in self.request.form:
            measureid=int(self.request.form['measureid'])
            return DB.Measure.objects.get(id=measureid)
        return None
    def DerivedMeasure(self):
        if 'derivedid' in self.request.form:
            derivedid=int(self.request.form['derivedid'])
            return DB.Percentage.objects.get(id=derivedid)
        return None
    def chartname(self):
        measure=self.Measure()
        if measure:
            return measure.name
        derived=self.DerivedMeasure()
        if derived:
            return derived.name
        return ''
    def min(self):
        if self.hasmax():
            return "0"
        return ""
    def max(self):
        derived=self.DerivedMeasure()
        measure=self.Measure()
        if self.hasmax():
            return "100"
        return ""
    def hasmax(self):
        derived=self.DerivedMeasure()
        measure=self.Measure()
        if derived:
            return True
        
        return False
    def cdata(self, content):
        return "<![CDATA[%s]]>"%content

class DynamicImageView(BrowserView):

    def __call__(self, *args, **kw):
        #delegate the actual image creation to child classes
        sent=StringIO()
        if self.request.has_key('grouping'):
            self.grouping=self.request['grouping']
        image=self.getImage()
        image.save(sent,'PNG')
        response=self.request.response        
        response.setHeader('Pragma', 'no-cache') 
        response.setHeader('Content-Type', 'image/png')
        
        response.write(sent.getvalue())
"""
class PieChartImage(DynamicImageView):
    
    def getImage(self):
        chart=PieChart()
        columns=[]
        if self.grouping=='measure':
            measures=DB.Measure.objects.all()
            for measure in measures:
                p=Column()
                p.name=measure.shortname
                values=DB.MeasurementValue.objects.filter(measure=measure)
                p.values=[]
                for v in values:
                    p.values.append(v.value)
                columns.append(p)
        else:
            for i in range(100):
                p=Column()
                p.values=(1+(i%5)*3,3+i,5)
                p.name='column %i'%i
                columns.append(p)

        chart.columns=columns
        chart.name='example'
        return chart.image()
"""