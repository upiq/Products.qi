from Products.Five.browser import BrowserView
from Products.qi.datacapture.file.uploads.uploadutils import makeFile
from Products.qi.util.lib.pyExcelerator import ImportXLS
from qi.sqladmin import models as DB
from Products.qi.datacapture.file import upload
import random
import os
from Products.qi.util.general import BrowserPlusView
from Products.qi.extranet.pages.success import Success
import os.path
from datetime import datetime
import Products.qi.extranet.types.handlers.django
from Products.qi.util.logger import logger


class DataUpload(BrowserPlusView):
    
    
    errors={}
    
    def __call__(self, *args, **kwargs): #may redirect on valid upload
        self.request['disable_border']=True
        self.update(*args, **kwargs)
        return self.index(*args,**kwargs)
    
    def update(self, *args, **kwargs):
        form=self.request.form
        self.errors={}
        if 'submit' in form:
            if self.validateForm(form):
                try:
                    #register a bunch of information about the file uploaded
                    if 'typename' in form:
                        name=form['typename']
                        classname=self.context.registeredtranslators[name]
                    else:
                        classname=None
                    classtype="transformed"
                    if classname is not None and classname.lower().startswith("sas:"):
                        classtype="sas"
                    fileobj=DB.File()
                    status=DB.UploadStatus()
                    filedata=form['file']
                    displayname,extension=filedata.filename.rsplit('.',1)
                    fileobj.displayname=filedata.filename.split('\\')[-1]
                    fileobj.name, fileobj.folder=makeFile(displayname,filedata, extension,classtype)
                    fileobj.project, fileobj.team=self.getDBProjectTeam()
                    fileobj.description="Importable data file"
                    fileobj.processed=None
                    fileobj.submitted=datetime.now()
                    fileobj.reportdate=datetime.now()
                    fileobj.save()
                    #create a tracker and mark it incomplete
                    #this will cause it to be picked up for processing
                    status.tracked=fileobj
                    status.project, status.team=self.getDBProjectTeam()
                    status.initiated=datetime.now()

                    status.translator=classname
                    status.status="Waiting to be processed"
                    status.complete=False
                    status.save()
                    target="status?fileid=%i"%status.tracked.id
                    self.doRedirect(target)
                except Exception, e:
                    logger.handleException(e)
                    self.doRedirect('Error.html')

        
    def usedTypes(self, cleanonteam=False):
        project, team=self.getProjectTeam()
        result={}
        if project is not None:
            if hasattr(project, 'translators'):
                for translator in project.translators:
                    result[translator]=translator
        if team is not None:
            if cleanonteam:
                result={}
            if hasattr(team, 'translators'):
                for translator in team.translators:
                    result[translator]=translator
        return [k for k in result.iterkeys()]
                
    #does not return first row                    
    def validateForm(self, form):
        if 'file' not in form:
            self.addError('file','Please upload a file')
            return False
        if form['file'] is None or form['file']=='':
            self.addError('file','No file sent, please try again')
            return False
        if len(self.usedTypes())>0 and 'typename' not in form:
            self.addError('typename', 'A file type must be specified')
            self.addError('base', 'there was a problem with the form')
            return False
        return True
        
    

    def url(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)
        
class UploadSuccess(Success):
    def target(self):
        return '%s/%s'%(self.context.absolute_url(),'import.html')
        
    def verb(self):
        return 'upload another file'