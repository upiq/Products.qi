from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from datetime import datetime
from django.core.paginator import Paginator
from Products.PythonScripts.standard import html_quote
from StringIO import StringIO

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
