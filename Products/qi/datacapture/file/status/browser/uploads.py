from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from datetime import datetime
import time
from django.core.paginator import Paginator
#from Products.qi.browser.ksswrapper import KSSAction, KSSReplaceWrapper, KSSInnerWrapper
from Products.PythonScripts.standard import html_quote
from StringIO import StringIO
from xlwt import Workbook, easyxf
from Products.qi.util.logger import logger

class UploadStatusView(BrowserPlusView):
    processFormButtons=('Restart',)
    clearform=False
    def validate(self, form):
        pass
    def action(self, form, action):
        restarted=self.getUpload()
        restarted.complete=False
        restarted.status="Restarted: waiting to be processed."
        restarted.initiated=datetime.now()
        restarted.save()
        self.doRedirect("status?fileid=%i"%restarted.tracked.id)
    def getUpload(self):
        uploadid=int(self.request.form.get('fileid',-1))
        result=None
        try:
            result=DB.UploadStatus.objects.select_related(depth=5).get(tracked__id=uploadid)
        except DB.UploadStatus.DoesNotExist:
            result=None
        #no transformations needed
        return result
    
    def errorlevel(self):
        upload=self.getUpload()
        if upload is None:
            return 10
        if not upload.complete:
            return -1
        errors=upload.uploaderror_set.all()
        subset=errors.filter(errorlevel__gt=6)
        if subset.count()>0:
            return 10
        subset=errors.filter(errorlevel__gt=0)
        if subset.count()>0:
            return 5
        return 0

    def download(self, tfile):
        if tfile is not None:
            format="%s/%s?fileid=%i"
            return format%(self.context.absolute_url(),"downloadfile",tfile.id)
        else:
            return "javascript:void(0)"
    def link(self, tfile):
        if tfile is not None:
            format="%s/%s?fileid=%i"
            return format%(self.context.absolute_url(),"status",tfile.id)
        else:
            return "javascript:void(0)"
    def history(self, measurementvalue):
        format="%s/%s?valueid=%i"
        return format%(self.context.absolute_url(),"ValueChanges",measurementvalue.id)
    def alldata(self):
        return DB.MeasurementValue.objects.all()
    def DB(self):
        return DB

class ProjectUploadsView(BrowserPlusView):
    #no process form buttons
    #no validation
    #no action
    def getUploads(self):
        statuses=DB.UploadStatus.objects.all().select_related(depth=3)
        dbproj,dbteam=self.getDBProjectTeam()
        statuses=statuses.filter(project=dbproj)
        if dbteam is None:
            statuses=statuses.filter(team__isnull=True)
        else:
            statuses=statuses.filter(team=dbteam)
        return statuses
    def getPendingUploads(self):
        uploads=self.getUploads()
        return uploads.filter(complete=False).order_by('-initiated')
    def getFinishedUploads(self):
        uploads=self.getUploads()
        complete=uploads.filter(complete=True).order_by('-initiated')
        #django doesn't seem to be able to shortcut this
        return [x for x in complete if (x.uploaderror_set.filter(errorlevel__gt=5).count()==0 and x.status.lower().find('error')==-1)]
    def getErrorUploads(self):
        uploads=self.getUploads()
        complete=uploads.filter(complete=True).order_by('-initiated')
        return [x for x in complete if (x.uploaderror_set.filter(errorlevel__gt=5).count()>0 or x.status.lower().find('error')>-1) ]
    def link(self, upload):
        format="%s/%s?fileid=%i"
        return format%(self.context.absolute_url(),"status",upload.tracked_id)
    def download(self, upload):
        format="%s/%s?fileid=%i"
        return format%(self.context.absolute_url(),"downloadfile",upload.tracked_id)

class DetailView(BrowserPlusView):
    clearform=False
    
    def getID(self, name):
        form=self.request.form
        try:
            result= int(form[name])
            return result
        except Exception, e:
            return -1
    
    def applyFilters(self, base):
        result=base
        form=self.request.form
        if 'fileid' in form:
            fileid=self.getID('fileid')
            if fileid>0:
                result=result.filter(tfile__id=fileid)
        if 'teamid' in form:
            teamid=self.getID('teamid')
            if teamid>0:
                result=result.filter(team__id=teamid)
        if 'measureid' in form:
            measureid=self.getID('measureid')
            if measureid>0:
                result=result.filter(measure__id=measureid)
        if 'period' in form:
            periodtext=form['period']
            try:
                period=datetime(*time.strptime(periodtext,'%m/%d/%Y')[:4]).date
                result=result.filter(itemdate=period)
            except TypeError:
                logger.logText('invalid period filter: %s, ignoring'%periodtext)
            

        if 'subid' in form:
            subid=self.getID('subid')
            if subid>0:
                result=result.filter(form__id=subid)
        
        
        return result
    def getPage(self):
        form=self.request.form
        if 'page' in form:
            try:
                return int(form['page'])
            except: 
                pass
        return 1
    def getBaseQuery(self):
        return DB.MeasurementValue.objects.filter(team__in=self.teams())
    def teams(self):
        dbproj,dbteam=self.getDBProjectTeam()
        if dbteam is not None:
            result= dbteam.team_set.all()
            result= result | DB.Team.objects.filter(id=dbteam.id)
        else:
            result = dbproj.team_set.all()
        if dbproj.hideinactiveteams : result = result.filter(active=True)
        return result
            
    def getCurrentDetails(self):
        basequery=self.getBaseQuery()
        query=self.applyFilters(basequery).order_by('itemdate')
        pagethingy=Paginator(query, 20)
        pagenum=self.getPage()
        return pagethingy.page(pagenum), pagethingy.page_range
    def history(self, measurementvalue):
        format="%s/%s?valueid=%i"
        return format%(self.context.absolute_url(),"ValueChanges",measurementvalue.id)
    def urlChangeOrAdd(self, key, value):
        form=self.request.form
        varformat="viewdata?%s=%s"
        changed=varformat%(key,value)
        result=changed
        varformat="&%s=%s"
        for fkey in form:
            if fkey!=key:
                result+=varformat%(fkey,form[fkey])

        return result
    def excelLink(self):
        form=self.request.form
        varformat="?%s=%s"
        result="exportexcel"
        for fkey in form:
            result+=varformat%(fkey,form[fkey])
            varformat="&%s=%s"
        return result
    def urlWithDifferentPage(self, pagenum):
        return self.urlChangeOrAdd('page',pagenum)
        
        
"""

class StatusKss(KSSAction):
    def getStatus(self):
        return None
        statusid=int(self.request.form['fileid'])
        return DB.UploadStatus.objects.get(tracked__id=statusid)
    def doKss(self, core):
        return
        status=self.getStatus()
        core.replaceInnerHTML('#statuszone',status.status)

class FollowupKss(KSSInnerWrapper):
    def condition(self):
        return False
        objectid=int(self.request.form['fileid'])
        watched=DB.UploadStatus.objects.get(tracked__id=objectid)
        if watched.complete and watched.uploadstatus_set.all().count()>0:
            return True
        return False
    def followup(self):
        objectid=int(self.request.form['fileid'])
        watched=DB.UploadStatus.objects.get(tracked__id=objectid)
        return watched.uploadstatus_set.all().latest('tracked_id')
    
    def getTarget(self):
        return 'followupzone'
        

class DetailsKss(KSSReplaceWrapper):
    def getTarget(self):
        return "detailsection"
    def getUpload(self):
        uploadid=int(self.request.form.get('fileid',-1))
        result=None
        try:
            result=DB.UploadStatus.objects.select_related(depth=5).get(tracked__id=uploadid)
        except DB.UploadStatus.DoesNotExist:
            result=None
        #no transformations needed
        return result

    def download(self, tfile):
        if tfile is not None:
            format="%s/%s?fileid=%i"
            return format%(self.context.absolute_url(),"downloadfile",tfile.id)
    def link(self, tfile):
        format="%s/%s?fileid=%i"
        return format%(self.context.absolute_url(),"status",tfile.id)
    def history(self, measurementvalue):
        format="%s/%s?valueid=%i"
        return format%(self.context.absolute_url(),"ValueChanges",measurementvalue.id)
    def alldata(self):
        return DB.MeasurementValue.objects.all()
    def DB(self):
        return DB
"""