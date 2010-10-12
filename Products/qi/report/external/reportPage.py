from Products.qi.util.general import BrowserPlusView
from Products.qi.util.ksswrapper import *
from qi.sqladmin import models as DB
import datetime
from Products.qi.util import utils
from calendar import month_name

def getReportStatus(report, url):
    if report.reportstate==0:
        return """
            <form
            action="%s"
            method="post">
            <input type=hidden name="reportid" value="%i"/>
            Not running
            <input type="button" class="reportrunner" value="run" />
            </form>
            """%(url, report.id)
    else:
        value={1:'Waiting to be run',
             2:'Running',
             3:'Delivering'}.get(report.reportstate, 'Unknown State')
        result= """
            <form>
            <input type=hidden name="reportid" value="%i"/>
            <span class='invoked'>%s</span>
            </form>
            """%(report.id,value)
        return result

def getFiles(report):
    return report.reportfile_set.all()

class ReportPage(BrowserPlusView):
    
    def getReports(self):
        dbproj=self.context.getDBProject()
        return dbproj.reporttrigger_set.all()
    
    def status(self, value):
        return {0:'Not running',
                1:'Waiting to be run',
                2:'Running',
                3:'Delivering'}.get(value, 'Unknown State')
        
class AddReportForm(BrowserPlusView):
    processFormButtons=('add',)
    def allProjects(self):
        catalog=self.context.portal_catalog
        brains=catalog.searchResults(meta_type='qiproject')
        return [brain.getObject() for brain in brains]
        
        
    
    def validate(self, form):
        self.requiredAvailable(DB.ReportTrigger.objects.all(), 'reportname',
            'reportname','report name')
        self.requiredInTable(DB.Project.objects.all(),'projectid', 'Project')
    
    def action(self, form, action):
        projectid=int(form['projectid'])
        project=DB.Project.objects.get(id=projectid)
        name=form['reportname']
        created=DB.ReportTrigger()
        created.reportname=name
        created.project=project
        created.reportstate=0
        created.save()
        

class UpdateRunningState(KSSInnerWrapper):
    def getTarget(self):
        reportid=self.context.request.form['reportid']
        return '%s-status'%reportid
        
    def buildHtml(self):
        reportid=int(self.context.request.form['reportid'])
        report=DB.ReportTrigger.objects.get(id=reportid)
        url='%s/%s'%(self.context.absolute_url(),'reports.html')
        return '%s'%(getReportStatus(report, url))

class ExpandBatches(KSSInnerWrapper):
    def getTarget(self):
        reportid=self.context.request.form['reportid']
        return '%s-details'%reportid
    
    def report(self):
        
        id=int(self.context.request.form['reportid'])
        return DB.ReportTrigger.objects.get(id=id)
    
class Batches(BrowserPlusView):
    processFormButtons=("Run",)
    clearform=False
    def report(self):

        id=int(self.context.request.form['reportid'])
        return DB.ReportTrigger.objects.get(id=id)    
    def validate(self, form):
        pass
    def action(self, form, action):
        report=self.report()
        report.reportstate=1
        report.lasttriggertime=datetime.datetime.now()
        report.save()
class CollapseBatches(KSSInnerWrapper):
    def getTarget(self):
        reportid=self.context.request.form['reportid']
        return '%s-details'%reportid
        
    def buildHtml(self):
        return """
<input type="hidden" name="reportid" value="%s" />
<input class="expandbatch" value="+" type="button"/>
Results"""%self.context.request.form['reportid']
        
class StartReport(KSSAction):
    def doKss(self,core):
        reportid=int(self.context.request.form['reportid'])
        report=DB.ReportTrigger.objects.get(id=reportid)
        if report.reportstate==0:
            report.reportstate=1
            report.lasttriggertime=datetime.datetime.now()
            report.save()

class Month:
    pass

def sortmonths(leftmonth, rightmonth):
    if leftmonth.month==-1:
        return -1
    if rightmonth.month==-1:
        return 1
    if rightmonth.year>leftmonth.year:
        return 1
    if leftmonth.year>rightmonth.year:
        return -1
    if rightmonth.number>leftmonth.number:
        return 1
    if rightmonth.number<leftmonth.number:
        return -1
    return 0
    

class TeamReports(BrowserPlusView):
    
    def months(self):
        result={}
        team=self.context.getDBTeam()
        for report in team.reportfile_set.all():
            batch=report.batch
            if not batch.approvalstate:
                continue
            date=batch.completiontime
            if date is not None:
                key=(date.year,date.month)
            else:
                key=None
            if key in result:
                month=result[key]
            else:
                month=Month()
                result[key]=month
                if date is not None:
                    month.number=date.month
                    month.name=month_name[month.number]
                    month.year=date.year
                else:
                    month.number=-1
                    month.name='No date '
                    month.year=0
                month.results=[]
            month.results.append(report)
        
        finalresult=[k for k in result.itervalues()]
        return self.sortlist(finalresult,sortmonths)


class ProjectReports(BrowserPlusView):
    
    def months(self):
        result={}
        project=self.context.getDBProject()
        triggers=project.reporttrigger_set.all()
        batches=DB.ReportBatch.objects.all().filter(report__in=triggers)
        allfiles=DB.ReportFile.objects.all().filter(batch__in=batches)
        reportfiles=allfiles.filter(team__isnull=True)
        for report in reportfiles:
            batch=report.batch
            if not batch.approvalstate:
                continue
            date=batch.completiontime
            if date is not None:
                key=(date.year,date.month)
            else:
                key=None
            if key in result:
                month=result[key]
            else:
                month=Month()
                result[key]=month
                if date is not None:
                    month.number=date.month
                    month.name=month_name[month.number]
                    month.year=date.year
                else:
                    month.number=-1
                    month.name='No date '
                    month.year=0
                month.results=[]
            month.results.append(report)
        
        finalresult=[k for k in result.itervalues()]
        return self.sortlist(finalresult,sortmonths)


class Batch(BrowserPlusView):
    processFormButtons=('ChangeState',)
    def batch(self):
        if 'id' in self.context.request.form:
            id=int(self.context.request.form['id'])
        else:
            return None
        return DB.ReportBatch.objects.get(id=id)
    
    def validate(self, form):
        self.required('id')
        self.required('approval')
    
    def action(self, form, action):
        batch=self.batch()
        self.clearform=False
        if action=='ChangeState':
            if form['approval']=='public':
                batch.approvalstate=True
            else:
                batch.approvalstate=False
        batch.save()
    