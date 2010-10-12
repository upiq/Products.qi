from BuildUpload import UploadBuilder
from DataGroups import AllData
from qi.sqladmin import models as DB
#this class doesn't do heavy lifting
#but rather holds the data used to process details of an upload


class Upload:
    def __init__(self, tracker):
        self.rows=[]
        self.errors={}
        self.warnings={}
        self.tracker=tracker
        self.dbproj=tracker.project
        self.dbteam=tracker.team
    def doImport(self, reporttype):
        reporttype=reporttype.strip()
        parts=reporttype.rsplit('.',1)
        module=__import__(parts[0])

        objname=parts[1]
        moduleparts=parts[0].split('.')[1:]
        for part in moduleparts:
            module=getattr(module, part)
        return getattr(module,objname)()
    def recordErrors(self):
        dberrors=self.tracker.uploaderror_set
        highesterrorlevel=0
        for key in self.errors.iterkeys():
            linenum, errorlevel=key
            array=self.errors[key]
            highesterrorlevel=max(highesterrorlevel,errorlevel)
            for error in array:
                
                newerror=DB.UploadError()
                newerror.rownum=int(linenum)
                #at most one error per line for now
                #combine them if this becomes a problem
                if isinstance(error, (list,tuple)):
                    newerror.message=error[0]
                else:
                    newerror.message=error
                newerror.status=self.tracker
                newerror.errorlevel=errorlevel
                newerror.save()
        if highesterrorlevel>5:
            self.tracker.status="Failed"
        self.tracker.save()
        return highesterrorlevel
    def validateRows(self):
        for row in self.rows:
            if row is not None:
                validation=row.validate()
                if validation is not None:
                    error="%s was missing or badly formatted on row %i"%(validation,row.rownum)
                    self.addError(row.rownum,error)
            else:
                self.addError(-1, 'File format is incorrect')
    
    
    def status(self, message):
        self.tracker.status=message
        self.tracker.save()
    def process(self):
        #make room for new errors
        classname=self.tracker.translator
        self.status("Finding data translate utility")
        
        if classname is None or classname.strip() == "":
            classname='Products.qi.datacapture.file.translate.default.PracticeTranslator'

        translator=self.doImport(classname)
        path="%s/%s"%(self.tracker.tracked.folder, self.tracker.tracked.name)
        self.status("Translating file.")
        translator.loadData(path)
        self.tracker
        temperrors=translator.getErrors()
        for x in temperrors:
            self.addError(x,temperrors[x])
        if self.hasErrors():
            self.fail()
        self.status("Compiling data rows.")
        self.rows=translator.getRows()
        self.status("Looking for malformed data.")
        self.validateRows()
        if self.hasErrors():
            return self.fail()
        builder=UploadBuilder(self)
        self.status("Locating required data.")
        builder.handleRequirements()
        if self.hasErrors():
            return self.fail()
        self.status("Attaching required data.")
        builder.translateRows()
        self.status("Preparing data for database.")
        self.data=AllData(self.tracker.tracked)
        self.data.addrows(self.translated)
        self.status("Running measure validation.")
        validation=self.data.runValidation()
        for rownum,errormessage,errorlevel in validation:
            self.addError(rownum,errormessage,errorlevel)
        errorlevel=self.recordErrors()
        if errorlevel>5:
            return False
        elif errorlevel>0:
            return self.warn()
        return self.succeed()
    
    def fail(self):
        self.recordErrors()
        return False
    def warn(self):
        self.status("Committing data to database.")
        for row, changeset in self.data.getAllEntries():
            row.save()
            for change in changeset:
                #rebind now
                change.value=row
                change.save()
        self.status("The import finished successfully (with warnings)")
        return True
    def succeed(self):
        #write our data
        self.status("Committing data to database.")
        for row, changeset in self.data.getAllEntries():
            row.save()
            for change in changeset:
                #rebind now
                change.value=row
                change.save()
        self.status("Finished successfully")
        return True

    def addError(self, key, value,errorlevel=10):
        realkey=(key, errorlevel)
        if self.errors.has_key(realkey):
            self.errors[realkey].append(value)
        else:
            self.errors[realkey]=[value,]

    def hasErrors(self):
        return len(self.errors)>0

    def getError(self, key):
        if self.errors.has_key(key):
            return self.errors[key]
        else:
            return None
        