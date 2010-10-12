from newlist import Message
from qi.sqladmin import models as DB
import datetime
import base64
import quopri
from Products.qi.util.logger import maillog as logger

class ImprovedMessage(Message):
    
    item=None
    baseheaderformat=u"""To: %s
From: %s
Subject: %s
Reply-To: %s
Mailed-By: %s
Sender: %s
Mailing-List: list %s; contact qiteamspace-owner@ursalogic.com 
Precedence: Bulk
List-Unsubscribe: <mailto:unsubscribe+%s@%s>
MIME-Version: 1.0"""
    
    singleheaderformat=u"""
Content-Type: %s
Content-Transfer-Encoding: %s%s

"""

    dispositionformat=u"\nContent-disposition: %s\n"

    noencodingformat=u"""
Content-Type: %s
Content-Disposition: %s

"""

    justcontent=u"""
Content-Type: %s

"""

    emailformat=u"""%s%s"""
    mutliheaderformat=u"""
Content-Type: %s

"""
    
    htmlblurb=u"""<br />
............................................................<br />
<b><font color="blue" size="5">%s Mailing List</font></b><br />
<font color="#5694A5">If you use the reply function of your email program, the reply will
be sent to <i>all</i> members of the mailing list.<br />
To reply to the sender only, use this email address:<br /></font>
%s <br />
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::<br />

%s
"""
    
    
    def buildHeaders(self,maillist,context):
        imaptool=context.IMapHost
        domain=imaptool.source_domain
        listname=maillist.listname

        user=imaptool.name_part
        fromname=self.fromemail
        if hasattr(self,'fromname'):
            fromname=self.fromname
        fromaddr=self.fromformat%(fromname,self.fromemail)
        replyaddr=self.replytoformat%(listname,user,listname,domain)
        mailedby=self.mailedbyformat%domain
        sender=self.addr_format%(listname,user,domain)
        
        subject=self.subjectformat%self.subject
        header=self.baseheaderformat%(replyaddr,fromaddr,subject,
                replyaddr,mailedby,sender,sender,listname,domain)
        return header

    def buildContent(self, maillist,context):
        self.plaintextfound=[]
        result=self.a(self.item,maillist)
        if len(self.plaintextfound)>0:
            self.contents=self.plaintextfound[0]
        else:
            self.contents="""
Due to the format of this email, the mail system could not archive it.
"""
        return result
    
    
    def a(self,item, mlist, reclevel=0,isAttachment=False):
        if item.is_multipart(): 
            header=self.mutliheaderformat%item['Content-Type']
            if header.lower().find("attach")>-1:
                isAttachment=True
            bodyparts=[self.a(k,mlist,reclevel+1, isAttachment) for k in item.get_payload()]
            boundary=item.get_boundary(None)
            if boundary is None:
                boundary='--=%i=--'%reclevel
                header=self.mutliheaderformat%(item['Content-Type']+'; boundary="%s"'%boundary)
            body="--"+boundary
            for part in bodyparts:
                body=body+part+u"\n--"+boundary
            body=body+u"--\n"
        else:
            header, body=self.buildBasePart(item, mlist, isAttachment)
        return header+body
        
    def buildBasePart(self,item,mlist, isattachment=False):
        encoding=item['Content-Transfer-Encoding']
        originaldisposition=item['Content-disposition']
        disposition=""
        if originaldisposition:
            disposition=self.dispositionformat%str(originaldisposition)
        if encoding is not None:
            header=self.singleheaderformat%(item['Content-Type'],
                encoding,
                disposition)
        else:
            if originaldisposition:
                header=self.noencodingformat%(item['Content-Type'],
                    originaldisposition)
            else:
                header=self.justcontent%item['Content-Type']
        body=item.get_payload()
        #skip blurb for attachments
        if isattachment:
            return header, body
        if item['Content-Type'] is not None:
            if item['Content-Type'].find("text/plain")>-1:
                #no encoding means potentially 8 bits.  BE WARNED
                if encoding is None:
                    encoding="8bit"
                text=self.decode(encoding, body)

                if text is not None:
                    #strip out any sort of anything before doing something
                    text=self.stripnotes(text)
                    self.plaintextfound.append(text)
                    if len(self.plaintextfound)<2:
                        text=self.bodyformat%(mlist.listname,self.fromemail,text)
                    body=self.encode(encoding, text)
            if item['Content-Type'].find("text/html")>-1:
                if encoding is None:
                    encoding="7bit"
                try:
                    htmltext=self.decode(encoding, body)
                except UnicodeDecodeError:
                    logger.logText("fixing invalid unicode guess for this email section")
                    htmltext=unicode(self.decode(encoding,body), '8bit')#default unicode type(already figured out)
                if htmltext is not None:
                    htmltext=self.stripnotes(htmltext)
                    htmltext=self.htmlblurb%(mlist.listname, self.fromemail, htmltext)
                body=self.encode(encoding, htmltext.encode('UTF-8'))
        return header, body

    def decode(self, encoding, data):
        logger.logText('decoding with encoding %s'%encoding)
        if encoding.find("7bit")>-1:
            return unicode(data,'ascii')
        if encoding.find("8bit")>-1:
            return unicode(data,'ascii','ignore')
        if encoding.find("base64")>-1:
            return unicode(base64.b64decode(data),'ascii','ignore')
        if encoding.lower().find("quoted-printable")>-1:
            return unicode(quopri.decodestring(data),'ascii','ignore')
        logger.logText("found other encoding %s"%encoding)
        return None
    
    def encode(self, encoding, text):
        if encoding.find("7bit")>-1:
            return text.encode('ascii','ignore')
        if encoding.find("8bit")>-1:
            return text.encode('ascii','ignore')
        if encoding.find("base64")>-1:
            return base64.b64encode(text)
        if encoding.lower().find("quoted-printable")>-1:
            return quopri.encodestring(text)
        #return SOMETHING in cases where we don't understand
        #shouldn't come up.
        #maybe raise an exception?
        return ""
        
    
    def save(self, mailinglist,isreply):
        unformattedsubject,reply=self.unformatsubject()
        thread=None
        if isreply and reply:
            threads=DB.MailThread.objects.filter(
                list=mailinglist,subject=unformattedsubject)
            if len(threads)==0:
                reply=False
            else:
                thread=threads[0]
        if not (reply and isreply): #not an else, see above exception
            thread=DB.MailThread()
            thread.list=mailinglist
            thread.subject=unformattedsubject
            thread.save()
        dbmess=DB.Message()
        dbmess.thread=thread
        dbmess.fromuser=self.fromemail
        dbmess.sent=datetime.datetime.now()
        dbmess.body=self.contents
        dbmess.save()
    def stripnotes(self, text):
        start='............................................................'
        end  ='::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::'
        if text.find(start)>-1:
            before, rest=text.split(start, 1)

            if rest.find(end)>-1:
                middle, after=rest.split(end, 1)
                return '%s\n%s'%(before, self.stripnotes(after))

            else:
                return text
        else:
            return text
