from Products.Five.browser import BrowserView
from qi.sqladmin import models as DB

resultxmlformat= \
"""<file>
    <status>
        %(status)s
    </status>
    <errorlevel>
        %(errorlevel)i
    </errorlevel>
    <complete>
        %(complete)s
    </complete>
    <errors>
        %(errors)s
    </errors>
    <warnings>
        %(warnings)s
    </warnings>
</file>"""

messageformat=\
"""<notification>
    <message>
        %(message)s
    </message>
    <source>
        %(source)s
    </source>
</notification>"""

class Status(BrowserView):
    def __call__(self, *args, **kw):
        form=self.context.request.form
        try:
            status=DB.UploadStatus.objects.get(tracked__id=form['fileid'])
        except:
            return ""
        errors=status.uploaderror_set.all()
        if len(errors)==0:
            errorlevel=0
        else:
            errorlevel=max(map(lambda x: x.errorlevel, status.uploaderror_set.all()))
        self.context.request.response.setHeader("Content-type","text/xml")
        self.context.request.response.setHeader("Pragma","no-cache")
        statusinfo={'status':status.status,
        'errorlevel':errorlevel,
        'complete':status.complete,
        'warnings': '',#self.getMessages(status,1,5),
        'errors': ''} #self.getMessages(status,6,10)}
        
        return resultxmlformat%statusinfo
        
    def getMessages(self, status, minval,maxval):
        result=""
        errors=status.uploaderror_set.filter(errorlevel__lte=maxval, errorlevel__gte=minval)
        for x in errors:
            result+=messageformat%{'message': x.message, 'source': x.rownum }
        return result
        