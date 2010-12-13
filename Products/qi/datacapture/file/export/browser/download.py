from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB

class Download(BrowserPlusView):

    def __call__(self,*args,**kw):
        if 'fileid' in self.request:

            #security goes here
            target=int(self.request['fileid'])
            filename=self.getFile(target)
            data=open(filename).read()
            displayname=self.baseQuery().get(
                id=target).displayname
            RESPONSE=self.request.response
            
            if filename.lower().endswith('.xls') or filename.lower().endswith('.xlsx'):
                RESPONSE.setHeader('Content-Type', 'application/excel')
                disposition='inline; filename="%s"'%displayname
            elif filename.endswith('.pdf'):
                RESPONSE.setHeader('Content-Type', 'application/pdf')
                disposition='inline; filename="%s.pdf"'%displayname
            elif filename.endswith('.xml'):
                RESPONSE.setHeader('Content-Type', 'application/vnd.ms-excel')
                disposition='inline; filename="%s"'%displayname
            else:
                return ""
            RESPONSE.setHeader("Content-Length",len(data))
            RESPONSE.setHeader('Content-disposition',disposition)
            RESPONSE.write(data)
        else:
            return ""
    
    def getFile(self,fileid):
        dbfile=self.baseQuery().get(id=fileid)
        return '%s/%s'%(dbfile.folder,dbfile.name) 
    
    def baseQuery(self):
        return DB.File.objects.all()