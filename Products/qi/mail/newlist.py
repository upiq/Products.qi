from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.qi.util.utils import getUsersForMailingList
from Products.qi.mail.tools.imaphost import IIMAP
import datetime
from qi.sqladmin import models as DB
from Products.qi.util.logger import maillog as logger
import re


class Message:
    
    toformat='"%s Mailing List" <%s>'
    fromformat='"%s" <%s>'
    replytoformat='"%s" <%s+%s@%s>'
    subjectformat='%s'
    mailedbyformat="%s"
    addr_format="%s+%s@%s"
    
    bodyformat=u"""
............................................................
%s Mailing List
If you use the reply function of your email program, the reply will be sent to all members of the mailing list.
To reply to the sender only, use this email address:
%s
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

%s
"""


    noreplyformat=u"""
............................................................
%s Mailing List
Replies to this mailing list have been disabled.  If you reply to this email, your reply will be ignored.
To reply to the sender of this email, use this address: 
%s
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

%s
"""
    
    headerformat=u"""Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
To: %s\nFrom: %s\nSubject: %s\nReply-To: %s\nMailed-By: %s
Sender: %s
Mailing-List: list %s; contact qiteamspace-owner@ursalogic.com 
Precedence: Bulk
List-Unsubscribe: <mailto:unsubscribe+%s@%s>"""
    emailformat=u"""%s

%s"""

    #set the following:
        #subject
        #fromemail
        #contents
    #optional:
        #fromname
    
    def build(self,maillist,context):
        header=self.buildHeaders(maillist, context)
        body=self.buildContent(maillist, context)
        self.almostEmail=self.emailformat%(header,body)
        #self.doublepercents()
        
    def buildHeaders(self, maillist,context):
        imaptool=context.IMapHost
        domain=imaptool.source_domain
        listname=maillist.listname
        user=imaptool.name_part
        fromname=self.fromemail
        if hasattr(self,'fromname'):
            fromname=self.fromname
        fromaddr=self.fromformat%(fromname,self.fromemail)
        sender=self.addr_format%(listname,user,domain)
        replyaddr=self.replytoformat%(listname,user,listname,domain)
        mailedby=self.mailedbyformat%domain
        subject=self.subjectformat%self.subject
        
        header=self.headerformat%(replyaddr,fromaddr,subject,
                replyaddr,mailedby, sender,sender,listname,domain)
        return header

    
    def buildContent(self, maillist, context):
        listname=maillist.listname
        body=self.bodyformat%(listname, self.fromemail,self.contents)
        if not maillist.replyable:
            body=self.noreplyformat%(listname, self.fromemail,self.contents)
        return body

    
    def doublepercents(self):
        result=""
        count=0
        for part in self.almostEmail.split('%'):
            count=count+1
            if count==2 or count==3:
                result=result+"%"+part
            elif count>3:
                result=result+"%%"+part
            else:
                result+=part
        self.almostEmail=result
    
    def send(self, address,mailinglist,context,emails):
        #print 'in send'
        imaptool=context.IMapHost
        sent=self.almostEmail#self.replytoformat%(listname,user,listname,domain)
        #mailhost=getUtility(IMailHost,context)
        mailhost=context.MailHost
        #print sent
        mailhost.send(str(sent), emails)
    
    def unformatsubject(self):
        reformats=( 're: ','re:',' re: ',
                    'RE: ','RE:',' RE: ',
                    'Re: ','Re:',' Re: ')
        unformattedsubject=self.subject
        reply=False
        for format in reformats:
            if unformattedsubject.startswith(format):
                unformattedsubject=unformattedsubject[len(format):]
                reply=True
                break
        lines=unformattedsubject.splitlines()
        unformattedsubject=""
        for line in lines:
            unformattedsubject+=line
        return unformattedsubject, reply
    
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
            
    def sendAll(self,mailingList, context):
        #print 'in sendAll'
        logger.logText("Sending message to %s"%mailingList.listname)
        userids=getUsersForMailingList(mailingList, context)
        mtool=getToolByName(context,'portal_membership')
        addresses=[mtool.getMemberById(x).getProperty('email',x) for x in userids]
        self.build(mailingList, context)
        self.send(None,mailingList,context, addresses)
            
    
