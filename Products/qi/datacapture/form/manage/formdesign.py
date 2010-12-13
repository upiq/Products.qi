from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB

class FormDesign(BrowserPlusView):
    processFormButtons=('save',)
    dbform=None
    def first(self):
        self.dbform=self.getForm()
    
    def generalUpdate(self):
        if self.dbform is not None:
            formmeasures=self.dbform.formmeasure_set.all().order_by('order')
        else:
            formmeasures=[]
        projmeasures=self.context.getDBProject().projectmeasure_set.all()
        self.curMeasures=[x.measure for x in formmeasures]
        self.allMeasures=[x.measure for x in projmeasures]
        self.availMeasures=sorted([x for x in self.allMeasures if x not in self.curMeasures])
    
    def validate(self, form):
        self.requiredInForm('measure')
        if self.hasErrors():
            self.errors['base']=["You must include at least one measure in this form.",]
        self.required('formname')
        if 'forwardwindow' in form and form['forwardwindow']!='':
            self.requiredInt('forwardwindow')
        if 'backwardwindow' in form and form['backwardwindow']!='':
            self.requiredInt('backwardwindow')
    
    def action(self, form, action):
        measures=form['measure']
        if isinstance(measures, (str, unicode)):
            measures=[measures]
        if self.dbform is None:
            print 'dbform was none'
            self.dbform=DB.Form()
        self.dbform.project=self.context.getDBProject()
        self.dbform.name=form['formname']
        self.dbform.qionly=False
        if 'qiconly' in form:
            self.dbform.qionly=True
        if 'forwardwindow' in form and form['forwardwindow']!='':
            self.dbform.daysforwardwindow=int(form['forwardwindow'])
        else:
            self.dbform.daysforwardwindow=None
        if 'backwardwindow' in form and form['backwardwindow']!='':
            self.dbform.daysbackwardwindow=int(form['backwardwindow'])
        else:
            self.dbform.daysbackwardwindow=None
        self.dbform.save()
        self.dbform.formmeasure_set.all().delete()
        order=1;
        for x in measures:
            formmeasure=DB.FormMeasure()
            formmeasure.measure=DB.Measure.objects.get(id=int(x))
            formmeasure.form=self.dbform;
            formmeasure.instructions="Type a value"
            formmeasure.order=order
            formmeasure.save()
            order=order+1
        self.doRedirect('ManageForms')
        #print 'got far enough'
    
    def getForm(self):
        #we already GOT one(from, for example, submitting a form)
        if self.dbform is not None:
            return self.dbform
        try:
            return DB.Form.objects.get(id=self.request.form['formid'])
        except Exception, e:
            print 'exception occured %s'%e
            return None
            
class AllForms(BrowserPlusView):
    processFormButtons=('delete.x','delete')
    
    def validate(self, form):
        if self.requiredInTable(self.context.getDBProject().form_set.all(),'deleted'):
            formobj=self.context.getDBProject().form_set.all().get(id=int(form['deleted']))
            if formobj.formsubmission_set.all().count()>0:
                self.addError('base','Users have submitted data with this form, it cannot be deleted')
    
    def action(self, form, action):
        deleted=DB.Form.objects.get(id=int(self.request.form['deleted']))
        deleted.delete()
    
    def allforms(self):
        return self.context.getDBProject().form_set.all()
    def linkfor(self, formobj):
        return '%s/DesignForm?formid=%i'%(self.context.absolute_url(), formobj.id)

class EstablishDates(BrowserPlusView):
    processFormButtons=('submit','delete.x')
    
    def existing(self):
        project=self.context.getDBProject()
        return DB.DataDate.objects.filter(project=project).order_by('period')
    
    def forms(self):
        return DB.Form.objects.filter(project=self.context.getDBProject()).order_by('name')
    
    def validate(self, form):
        if 'submit' in form:
            self.required('name')
            self.requiredDate('date')
            self.requiredInt('formid')
            if not self.hasErrors():
                project=self.context.getDBProject()
                name=form['name']
                formid=int(form['formid'])
                date=self.buildDate(form['date'])
                base=DB.DataDate.objects.filter(project=project)
                if formid>-1:
                    base=base.filter(form__id=formid)
                else:
                    base=base.filter(form__isnull=True)
                if base.filter(period=date).count()>0:
                    self.addError('date','that date is in use')
                if base.filter(name=name).count()>0:
                    self.addError('name','that name is in use')
        if 'delete.x' in form:
            self.requiredInt('deleted')
    def action(self, form, action):
        if action=='submit':
            created=DB.DataDate()
            formid=int(form['formid'])
            if formid>-1:
                formobj=DB.Form.objects.get(id=formid)
            else:
                formobj=None
            created.project=self.context.getDBProject()
            created.period=self.buildDate(form['date'])
            created.name=form['name']
            created.form=formobj
            created.save()
        if action=='delete.x':
            delid=int(form['deleted'])
            deleted=DB.DataDate.objects.get(id=delid)
            deleted.delete()
    
        
        