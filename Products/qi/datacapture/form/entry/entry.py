from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from Products.CMFCore.utils import getToolByName
import AccessControl
from datetime import datetime, date, timedelta
from django.db import connection
from Products.qi.datacapture.validation.rules import Rule
from Products.qi.datacapture.validation.validationrules import buildRule
from qi.sqladmin.DataModels import File
from Products.qi.util.logger import logger

class MeasureDates(BrowserPlusView):
    processFormButtons= ('create', )
    clearform= False
    
    def action(self, form, action):
        inputform = form['inputform']
        period = form['period']
        url = "periodmeasures.html?inputform=%s&period=%s"%(inputform, period)
        self.doRedirect(url)
        
    def validate(self, form):
        self.requiredDate('period', 'Period')
    
    #Gets the dates for the measures associated with the given form   
    def getMeasureDates(self):
        """formid = self.request.form['inputform']

        output=[]
        
        measureset = DB.FormMeasure.objects.filter(form=formid)
        ids = [x.measure.id for x in measureset]
        
        mvals = DB.MeasurementValue.objects.filter(measure__id__in=ids, \
            team=self.context.getDBTeam())
        """
        formid = int(self.request.form['inputform'])
        mvals=DB.DataDate.objects.filter(project=self.context.getDBProject,form__id=formid).order_by('-period')
        if mvals.count()==0:
            mvals=DB.DataDate.objects.filter(project=self.context.getDBProject(), form__isnull=True).order_by('-period')
        if mvals.count()>1:
            mvals=[x for x in mvals if self.inwindow(x.period)]
        #this line is a mess it needs to go
        output=[{'period':j.period.strftime("%m/%d/%Y"),
            'name':j.name,
            'id':j.id,
            'isnew':DB.FormSubmission.objects.filter(
                form__id=formid,
                reportdate=j.period,
                team=self.context.getDBTeam()).count()==0} for j in mvals]
        """
        output = list(set(output))
        output.sort()
        """
        return output
    
    def inwindow(self, date):

        #we'll attach the current time to the date for compirso
        #date=datetime.combine(date, datetime.time(0))
        #give a huge threshold so we can do date comparison
        forwarddate=datetime.max.date()
        dbform=DB.Form.objects.get(id=self.request.form['inputform'])
        if dbform.daysforwardwindow is not None:
            forwarddate=(timedelta(dbform.daysforwardwindow)+datetime.now()).date()
        if self.context.getDBTeam().enddate is not None:
            forwarddate=min(forwarddate,self.context.getDBTeam().enddate)
        if date>forwarddate:
            return False
        
        #set a very Very reasonable threshold for the earliest someone could submit data
        backwarddate=datetime.min.date()
        if dbform.daysbackwardwindow is not None:
            backwarddate=(datetime.now()-timedelta(dbform.daysbackwardwindow)).date()
        if self.context.getDBTeam().startdate is not None:
            backwarddate=max(backwarddate, self.context.getDBTeam().startdate)
        if date<backwarddate:
            return False
        return True
            
    
    #For default value in the create period field.    
    def getCurrentTime(self):
        return datetime.now().strftime("%m/01/%Y")
    
    #For display purposes 
    def getFormName(self):
        formid = self.request.form['inputform']
        theform = DB.Form.objects.get(id=formid)
        return theform.name


class FakeObj(object):
    pass

class EntryList(BrowserPlusView):
    processFormButtons= ('save','confirm')
    clearform= False
    errors={}
    maxError=0
    
    def action(self, form, action):
        self.changeMeasures(form)
        
    def validate(self, form):
        validated = True
        self.maxError=0
        self.warnings={}
        ignored=('save','period','inputform','confirm')
        valuetable={}
        for i in form:
            if i not in ignored:
                measure = DB.Measure.objects.get(id=int(i))
                fakeobject=FakeObj()
                fakeobject.latestdate=FakeObj()
                fakeobject.latestdate.value=form[i][0]
                valuetable[measure.shortname]=fakeobject
        for i in form:
            if i not in ignored:
                measure = DB.Measure.objects.get(id=int(i))

                rule = buildRule(measure.validation)
                validationresult = rule.validate(form[i][0], valuetable)
                self.maxError=max(self.maxError,validationresult)
                if validationresult>0:
                    if validationresult>5:
                        self.addError(i, rule.getMessage())
                        validated = False
                    if validationresult<6 and 'confirm' not in form:
                        self.addError(i, 'Warning: '+rule.getMessage())
                        validated=False
                    
        form['submitted'] = validated   
       
    #tells the user whether everything was submitted ok             
    def isSubmitted(self, form):
        if 'submitted' in form:
            return form['submitted']
        else:
            return False
    
    def getdate(self):
        form=self.request.form
        return DB.DataDate.objects.get(id=int(form['period']))
    
    #The meat of actually changing the measure values and annotation. 
    def changeMeasures(self, form):
        args = form
        today = datetime.now().date()
        #period = args['period'].split("/")
        idate = self.getdate().period
        #idate = date(int(period[2]), int(period[0]), int(period[1]))
        mform = DB.Form.objects.get(id=int(args['inputform']))
        formsubmit = DB.FormSubmission.objects.create( \
            form=mform, reportdate=idate, team=self.context.getDBTeam())
        ignored=('save','period','inputform','confirm','submitted')
        for i in args:
            if i not in ignored:
                
                m = DB.Measure.objects.get(id=int(i))

                
                try:
                    mv= DB.MeasurementValue.objects.get(measure=m, itemdate=idate, team=self.context.getDBTeam())

                    self._saveToMeasurementChange(mv, mv.value, mv.annotation, args[i][0], \
                          args[i][1], mv.reportdate, mv.tfile, mv.form)
                          
                    mv.itemdate=idate
                    mv.reportdate=today
                    mv.value=args[i][0]
                    mv.annotation = args[i][1]
                    mv.team=self.context.getDBTeam()
                    mv.form=formsubmit
                    mv.save()
                    
                except DB.MeasurementValue.DoesNotExist:
                    mv = DB.MeasurementValue.objects.create( \
                        measure=m, value=args[i][0], reportdate=today, itemdate=idate)
                    mv.annotation = args[i][1]
                    mv.team=self.context.getDBTeam()
                    mv.form = formsubmit
                    mv.save()

                    #self._saveToMeasurementChange(mv, None, None, args[i][0], args[i][1], \
                    #    mv.reportdate, None, formsubmit)
                except Exception, e:
                    print 'error occurred:'
                    logger.handleException(e)
                    
                                           
    #Private function to update the measurement change table so we don't lose data
    def _saveToMeasurementChange(self, mv, oldvalue, oldanno, newvalue, newanno, reportdate, tfile, form):
        time = datetime.now()
        mc = DB.MeasurementChange.objects.create(value=mv, \
                                                newvalue=newvalue, \
                                                newannotation=newanno, \
                                                oldvalue=oldvalue, \
                                                oldannotation=oldanno, \
                                                changedon=time, \
                                                tfile=tfile, \
                                                reportdate=reportdate, \
                                                form=form)
        mc.save()
                       
    #Get all the measures for the working form in the selected period.
    def getMeasuresForForm(self):
        form = self.request.form['inputform']
        formmeasure = DB.FormMeasure.objects.filter(form=form).select_related(depth=1).order_by('order')
        return formmeasure
    
    #Gets the value for the given measure, to display in the periodmeasures table.
    def getValueForMeasure(self, measure):
        form=self.request.form
        #retain existing form information
        if str(measure.id) in form:
            return dict(measure=measure.name,value=form[str(measure.id)][0],annotation=form[str(measure.id)][1])
        try:
            #period = self.request.form['period'].split("/")
            #idate = datetime(int(period[2]), int(period[0]), int(period[1]))
            idate=self.getdate().period
            result = DB.MeasurementValue.objects.get(measure=measure, team=self.context.getDBTeam(), itemdate=idate)
            return dict(measure=measure, value=result.value, annotation=result.annotation)
        except DB.MeasurementValue.DoesNotExist:
            return dict(measure=measure, value='', annotation='')
       
        return dict(measure=measure, value=result.value, annotation=result.annotation)
    def getPreviousValueForMeasure(self, measure):
        form=self.request.form
        try:
            #period = self.request.form['period'].split("/")
            #idate = datetime(int(period[2]), int(period[0]), int(period[1]))
            idate=self.getdate().period
            result = DB.MeasurementValue.objects. \
                filter(measure=measure, team=self.context.getDBTeam(), itemdate__lt=idate). \
                latest("itemdate")
            return dict(measure=measure, value=result.value, annotation=result.annotation, itemdate=result.itemdate)
        except DB.MeasurementValue.DoesNotExist:
            return dict(measure=measure, value='None', annotation='', itemdate=None)

        
    #Just for displaying purposes
    def getFormName(self):
        formid = self.request.form['inputform']
        theform = DB.Form.objects.get(id=formid)
        return theform.name
        

        
        
class PickForm(BrowserPlusView):
    def hasChildren(self):
        team=self.context.getDBTeam()
        if team.team_set.all().count()>0:
            return True
    def children(self):
        from Products.qi.util.utils import getTeamsInContext
        return getTeamsInContext(self.context)
    
    #Lists all forms for the project
    def getForms(self):
        project=self.context.getDBProject()
        dbteam=self.context.getDBTeam()
        forms = DB.Form.objects.filter(project=project.id)
        if self.user()!=dbteam.qic:
            forms=forms.filter(qionly=False)
        
        return forms
    
    def canEnterData(self, team):
        mtool = self.context.getProject().portal_membership
        checkPermission = mtool.checkPermission
        return checkPermission('Enter Data', self.context.getProject())
    
    def checkProjectManager(self):
        mtool = self.context.getProject().portal_membership
        checkPermission = mtool.checkPermission
        return checkPermission('Modify portal content', self.context.getProject())
