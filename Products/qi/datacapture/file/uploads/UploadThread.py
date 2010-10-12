from threading import Thread, currentThread
from qi.sqladmin import models as DB
import Upload
import time
from Products.qi.util.logger import importlog as logger

class UploadListener(Thread):
    def __init__(self):
        Thread.__init__(self)
        logger.logText("preparing data import service")
        self.owner=currentThread()
    
    def currentImport(self):
        incomplete=DB.UploadStatus.objects.filter(complete=False)
        nonsas=incomplete.exclude(translator__istartswith="sas:")
        nulled=incomplete.filter(translator__isnull=True)
        possible=nonsas | nulled
        result=possible.order_by("initiated")
        
        if len(result)>0:
            return result[0]
        else:
            return None
    
    def processOne(self):
        current=None
        try:
            current=self.currentImport()
            if current is None:
                time.sleep(15.0)
                return
            logger.logText("processing item %i"%current.tracked.id)
            current.status="starting"
            #DELETE EVERYTHING, no need to retain old error messages
            current.uploaderror_set.all().delete()
            current.save()
            upload=Upload.Upload(current)
            upload.process()
            #we don't really care here what the result of that process was
            current.complete=True
            current.save()
        except Exception,e :
            logger.handleException(e)
            if current is not None:
                current.complete=True
                current.status="""A system error has occurred,
                    causing the data import to be cancelled. 
                    Please notify a project manager or QI TeamSpace technical support. 
                    You will need to reimport this file after the system problem has been corrected"""
                current.save()
            time.sleep(15.0)
        return
    
    def run(self):
        from Products.qi.util.thread import profile_on
        #profile_on()
        logger.logText("running import service")
        while self.owner.isAlive():
            self.processOne()