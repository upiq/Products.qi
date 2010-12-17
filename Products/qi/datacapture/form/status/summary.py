from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from xlwt import *
from StringIO import StringIO

class Linkable(object):
    def __init__(self, text, href):
        self.text=text
        self.href=href
    def __str__(self):
        return self.text
    def __unicode__(self):
        return self.text
    def __repr__(self):
        return self.text

class PickForm(BrowserPlusView):
    def first(self):
        self.loadForms()
        if len(self.forms)==1:
            self.doRedirect('formstatus?formid=%s'%self.forms[0].id)
    def loadForms(self):
        project=self.context.getDBProject()
        self.forms=project.form_set.all()

class DateSummary(object):
    teams=[]
    date=None
    name=""

def cmpteam(teama,teamb):
    return cmp(teama.name.lower(), teamb.name.lower())
    
def cmpsummary(summary1,summary2):
    date1,date2=summary1.date, summary2.date
    if date1 is None:
        return -1
    if date2 is None:
        return 1
    return cmp(date1,date2)
    
class SubmissionInfo:
    def __init__(self, team, submitted, newest, oldest):
        self.team=team
        self.submitted=submitted
        self.newest=newest
        self.oldest=oldest
    def __cmp__(self, other):
        return cmp(self.team.name.lower(),other.team.name.lower())
        
class SubmissionDate:
    def __init__(self,date, name):
        self.date=date
        self.name=name
        self.info=[]
        self.count=0
    def addTeam(self, team,submitted, newest=None, oldest=None):
        self.info.append(SubmissionInfo(team,submitted, newest,oldest))
        if submitted:
            self.count+=1
    def dosort(self):
        self.info.sort()
    def __cmp__(self, other):
        #default sort order is recent to old
        return cmp(other.date, self.date)

class ReportInfo(object):
    team=None
    teamid=None
    submissioncount=None
    date=None
    globalname=None
    localname=None
    oldest=None
    newest=None
    def __init__(self, row, form=None):
        self.teamid, self.team, self.submissioncount,self.date=row[:4]
        self.globalname,self.localname, self.newest=row[4:]
        try:
            self.oldest=DB.FormSubmission.objects.filter(team__id=self.teamid, form=form).order_by("submittime")[0].submittime.date()
        except IndexError:
            self.oldest=self.newest
            self.newest=None
        if self.oldest==self.newest:
            self.newest=None
        self.datename=self.localname or self.globalname or self.date
class FakeReportInfo(ReportInfo):
    def __init__(self,team):
        self.team=team
        self.submissioncount=0

class FormStatus(BrowserPlusView):
    def first(self):
        self.loadForm()
        self.runquery()
        print self.dates #TODO:remove/debug
        #self.loadDates()
        #self.loadTeams()
    
    def runquery(self):
        from Products.qi.util.utils import testquery
        project=self.context.getDBProject()
        data=[ReportInfo(x, self.form) for x in testquery("formdates", project_id=project.id, form_id=self.form.id)]
        if project.hideinactiveteams:
          self.teams=project.team_set.filter(active=True)
        else:
          self.teams=project.team_set.all()
#HERE
        self.targetcount=self.form.formmeasure_set.all().count()
        self.dates={}
        self.actualdates={}
        for record in data:
            teamdic=self.dates.get(record.date,(None,{}))[1]
            teamdic[record.team]=record
            self.dates[record.date]=(record.datename,teamdic)
        for otherdate in self.definednames():
            self.dates[otherdate[0]]=self.dates.get(otherdate[0],(otherdate[1],{}))
        
    
    def reportfor(self,team, period):
        print team, self.dates.get(period,('',{}))
        return self.dates.get(period,('',{}))[1].get(team,FakeReportInfo(team))
    def colorfor(self, team,period):
        count=self.reportfor(team, period).submissioncount
        print vars(self.reportfor(team, period))
        if count==0:
            return 'background-color:#FFAAAA'
        elif count<self.targetcount:
            return 'background-color:#FFFF44'
        else:
            return 'background-color: #AAFFAA'
            
    def definednames(self):
        project=self.context.getDBProject()
        localnames=DB.DataDate.objects.filter(project=project, form=self.form)
        if localnames.count()>0:
            return [(x.period,x.name) for x in localnames]
        globalnames=DB.DataDate.objects.filter(project=project, form__isnull=True)
        return [(x.period,x.name) for x in globalnames]
    
    def loadForm(self):
        formid=self.request.form['formid']
        self.form=DB.Form.objects.get(id=formid)
    
    def loadDates(self):
        project=self.context.getDBProject()
        teams=project.team_set.filter(active=True)
        dates={}
        for team in teams:
            submissions=team.formsubmission_set.filter(form=self.form)
            for submission in submissions:
                try:
                    name=DB.DataDate.objects.get(project=project, period=submission.reportdate,form=self.form).name
                except DB.DataDate.DoesNotExist:
                    try:
                        name=DB.DataDate.objects.get(project=project, period=submission.reportdate, form__isnull=True).name
                    except DB.DataDate.DoesNotExist:
                        name=submission.reportdate
                dates[submission.reportdate]=SubmissionDate(submission.reportdate, name)
        dates=sorted(dates.values())
        for x in dates:
            for y in teams:
                matches=DB.FormSubmission.objects.filter(
                    team=y,
                    form=self.form,
                    reportdate=x.date).order_by('submittime')
                if matches.count()>0:
                    oldest=matches[0]
                    newest=matches[matches.count()-1]
                    fmt="%m/%d/%Y"
                    oldstr=oldest.submittime.strftime(fmt)
                    if oldest.id==newest.id:
                        newstr=None
                    else:
                        newstr=newest.submittime.strftime(fmt)
                    
                    x.addTeam(y, True, newstr, oldstr)
                else:
                    x.addTeam(y,False)
            #sort the teams alphabetically 
            x.dosort()  
        self.dates=dates  
            
        
    
    def loadTeams(self):
        project=self.context.getDBProject()
        teams=project.team_set.all()
        if project.hideinactiveteams:
	       teams=teams.filter(active=True)
        #dates=project.datadate_set.all()
        dates={}
        for x in teams:
            try:
                lastSubmission=x.formsubmission_set.filter(form=self.form).latest('reportdate').reportdate
            except DB.FormSubmission.DoesNotExist:
                lastSubmission=None
            if lastSubmission not in dates:
                dates[lastSubmission]=[]
            dates[lastSubmission].append(x)
        summaries=[]
        
        for x in dates:
            data=dates[x]
            added=DateSummary()
            if x is not None:
                try:
                    added.name=DB.DataDate.objects.get(project=project, period=x).name
                except DB.DataDate.DoesNotExist:
                    added.name=x
                added.date=x
            else:
                added.name=""
                added.date=None
            added.teams=sorted(data, cmpteam)
            summaries.append(added)
        self.summaries=sorted(summaries,cmpsummary)


class Roster(BrowserPlusView):
    """a list of all practices with 
        region, assigned QIC, IPIP application date, 
        and month and year of first and last submissions for each data form;
        available to view online and download into Excel."""
    _forms=None
    datafor=None
    def teams(self):
        self.loadExistingRecords()
        """yeilds a list of (list of data) for each team in the current project structured based on what should be in this report"""
        form=self.request.form
        if 'parentid' in form:
            result=[self.buildteam(team) for team 
                in DB.Team.objects.get(id=int(form['parentid'])).team_set.all().order_by('name') 
                if self.activeFilter(team)]
        else:
            result= [self.buildteam(team) for team\
            in self.context.getDBProject().team_set.all().order_by('name')\
            if self.activeFilter(team)]
        return result
    def activeFilter(self, team):
        if self.context.getDBProject().hideinactiveteams:
            return team.active
        return True
    def loadExistingRecords(self):
        if self.datafor:
            return
        self.datafor={}
        from Products.qi.util.utils import testquery
        project=self.context.getDBProject()
        data=testquery("rosterinfo", project_id=project.id)
        for x in data:
            self.datafor[(x[0],x[1])]=x[2]
    def forms(self):
        if self._forms:
            return self._forms
        self._forms= DB.Form.objects.filter(project=self.context.getDBProject())
        return self._forms
    def buildteam(self, team):
        """generate one team's basic data"""
        result=[team.name, 
            self.getQICInfo(team.qic),
            team.startdate, 
            self.getPracticeID(team), 
            self.getRegion(team),
            self.getStatus(team),
            self.getStatusNotes(team)]
        for x in self.forms():
            result.append(self.datafor.get( (team.id, x.id), "None"))
            """
            submissions=x.formsubmission_set.filter(team=team)
            try:
                last=submissions.latest('reportdate').reportdate
                first=submissions.order_by('reportdate')[0].reportdate
                result.append( '%s/%s - %s/%s'%(first.month, first.year,last.month, last.year))
            except DB.FormSubmission.DoesNotExist:
                result.append('None')"""
        #print result
        return result
    def getPracticeID(self, team):
        nicknames=team.teamidentifier_set.all()
        print 'team', team
        for x in nicknames:
            try:
                result= int(x.value)
                print 'good', result
                return result
            except (ValueError):
                print 'bad',x
        return None
    def getStatus(self, team):
        try:
            return DB.MeasurementValue.objects.filter(team=team, measure__shortname="DataStatus").latest("itemdate").value
        except DB.MeasurementValue.DoesNotExist:
            return "No record"
    def getStatusNotes(self, team):
        try:
            DB.MeasurementValue.objects.filter(team=team, measure__shortname="DataStatusNotes").latest("itemdate").value
        except DB.MeasurementValue.DoesNotExist:
            return "No record"
    def getRegion(self,team):
        if team.parent:
            par=team.parent
            return Linkable(par.name,'%s/teamroster?parentid=%i'%(self.context.absolute_url(),par.id))
        return ""
    def getQICInfo(self, qicid):
        if getattr(self,'userTool',None) is None:
            self.userTool=self.context.acl_users
        if not qicid:
            return 'No assigned qic'
        userinfo=self.userTool.getUserById(qicid)
        if userinfo and hasattr(userinfo,'getProperty'):
            return userinfo.getProperty('fullname')
        return qicid

        return result
    def indices(self):
        """return the structure of the rows"""
        result= ["Team Name","Assigned QIC","Application Date","PracticeID", "Region","Data Status","Data Status Notes"]
        for form in self.forms():
            result.append('%s submissions'%form.name)
        return result

class ExcelRoster(Roster):
    def __call__(self,*args,**kw):
        response=self.request.response
        response.setHeader("Content-type","application/vnd.ms-excel")
        response.setHeader("Content-disposition","attachment;filename=teamroster.xls")
        return self.buildExcel()
    def buildExcel(self):
        resultdata=StringIO()
        resultbook=Workbook()
        sheet=resultbook.add_sheet('Team Roster')
        self.writesheet(sheet)
        resultbook.save(resultdata)
        return resultdata.getvalue()
    def writesheet(self, sheet):
        for x, value in enumerate(self.indices()):
            sheet.write(0,x, value)
        for y, row in enumerate(self.teams()):
            for x, value in enumerate(row):
                sheet.write(y+1,x,str(value))
        
                
