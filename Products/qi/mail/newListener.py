from threading import Thread, currentThread
import time
import ZODB, transaction
import ZEO.ClientStorage
from ZODB import FileStorage, DB as ZopeDB
from zope.component import getUtility
from zope.component import getSiteManager
from Products.qi.mail.tools.imaphost import IIMAP
from Products.CMFCore.utils import getToolByName
from qi.sqladmin import models as DB
from Products.qi.extranet.types.interfaces import IProject, ITeam
#from Products.qi.mail.mailinglist import MailBatch
from Products.CMFCore.utils import getToolByName
import datetime
import re
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.BaseRequest import RequestContainer
from Products.CMFPlone.Portal import PloneSite 
from Products.MailHost.interfaces import IMailHost
from Products.qi.util.utils import getProjectsInContext, getTeamsInContext
from Products.qi.util.logger import maillog as logger
from Products.qi.util.config import ZEO_ADDRESS

zopeport=9995
from Products.qi.util.thread import profile_on

from Products.qi.mail.extendedlist import ImprovedMessage as Message

def imapEnabled(context):
    tool = getUtility(IIMAP,context=context)
    if tool.disabled:
        return False
    return True

class MailListener(Thread):
    owner=currentThread()
    connection=None
    db=None
    
    

    
    def globalBegin(self):
        #profile_on()
        #we'd simply like to make sure that we don't break anything by profiling this thread
        #we can still clear it later?
        logger.logText("booting up the mail listener")
        zeoaddr = ZEO_ADDRESS.split(':')        # hostname:portnum
        zeoaddr = (zeoaddr[0], int(zeoaddr[1])) # port: str->int
        self.storage=ZEO.ClientStorage.ClientStorage(zeoaddr)
        self.db=ZopeDB(self.storage)
        self.connection=self.db.open()
        self.root=self.connection.root()
        self.app=self.root['Application']

        
    def getContext(self, app):
        resp = HTTPResponse(stdout=None)
        env = {
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'%i'%zopeport,
            'REQUEST_METHOD':'GET'
            }
        req = HTTPRequest(None, env, resp)
        myapp= app.__of__(RequestContainer(REQUEST = req))
        try:
            return myapp.qiteamspace
        except:
            return myapp.Testbed        
            #if we can't find either of those propogate exception to thread level
    
    def begin(self):
        #print dir(self.db)
        #self.connection=self.db.open()
        #self.connection.open()
        #self.root=self.connection.root()
        #self.app=self.root['Application']
        transaction.begin()
        self.context2=self.getContext(self.app)
        
    def end(self):
        transaction.commit()
        #self.connection.close()
    
    def run(self):
        try:
            self.processMail()
        except Exception, e:
            #self.connection.close()
            transaction.abort()
            logger.handleException(e)


    def processMail(self):
        #print 'newListener run'
        self.globalBegin()
        self.tool = self.context.IMapHost
        i=0
        self.end()
        while self.owner.isAlive() and not self.tool.disabled:
            i+=1
            #don't just delay 20 seconds, as this will make it 
            #so we won't exit quickly after the server is control-c'd
            if i==20:
        
                i=0
        
                self.begin()
                self.tool = self.context2.IMapHost
                self.rebroadcastmail()
                self.end()
            #a bit of delay is fine, we don't want to waste server power
            time.sleep(3)
            
    def rebroadcastmail(self):
        #print 'rebroadcastmail'
        items=self.tool.getNextGroup('INBOX')
        #print 'doing resend'
        for item in items:
            #print 'found an item'
            self.handleMail(item)
    


    def handleMail(self, item):
        #print 'handleMail'
        subject=item['subject']
        frominfo=item['from']

        returnpath=item["Return-Path"]
        toinfo=item['to']
        ccinfo=item['cc']
        forinfo=item['received']
        listsearch=(toinfo,ccinfo,forinfo)
        logger.logText("received [%s] from <%s> to <%s>"%(subject, frominfo,toinfo))
        fromaddr=self.getAddress(frominfo)
        nameandemail=self.extractEmailAndName(frominfo)
        if not nameandemail:
            nameandemail=self.extractEmailAndName(returnpath)
            if not nameandemail:
                return self.throwAway(item,
                    'the from address could not be determined')
        if not fromaddr:
            fromaddr=self.getAddress(returnpath)
            if not fromaddr:
                return self.throwAway(item,
                    'the from address could not be determined from %s or %s'%(frominfo,returnpath))
        mailinglist=None
        for info in listsearch:
            if mailinglist is None:
                mailinglist=self.getMailingAddress(info)
        if not mailinglist:
            return self.throwAway(item, 'mailing list could not be found for %s'%str(listsearch))
        sent=Message()
        sent.subject=subject
        if self.rejectedReply(sent,mailinglist):
            return self.throwAway(item,"Message appeared to be automated reply")
        if not mailinglist.replyable:
            return self.throwAway(item,
                'reply was invalid as %s does not allow replies'%mailinglist.listname)
        body=self.getBody(item)
        if body is None:
            return self.throwAway(item,'body was not retreived')
        



        sent.fromemail=nameandemail[1]
        sent.fromname=nameandemail[0]
        sent.contents=body
        sent.item=item
        projectorteam=self.getProjectOrTeam(mailinglist, self.context2)
        sent.sendAll(mailinglist, projectorteam)
        sent.save(mailinglist,True)

        return False

        
    def getAddress(self, fromblock):
        return fromblock
    
    def throwAway(self, message, reason='No reason provided'):
        
        rejectAddresses=[x.strip() for x in self.context2.IMapHost.bounce_addr.split(',')]
        sender=self.context2.MailHost
        portal = getToolByName(self.context2, 'portal_url').getPortalObject()
        from_addr = portal.getProperty('email_from_address', '')
        if not from_addr:
            from_addr = 'admin@qiteamspace.com'

        if len(rejectAddresses)>0:
            errormessage="From: <%s>\nTo: %s\nSubject: Rejected mail\n\n the"\
                         " following was rejected because %s\n\n%s" % (
                            from_addr,
                            'Nobody',
                            reason,
                            str(message))
            print errormessage
            sender.send(errormessage,rejectAddresses)
        
        logger.logText('System is discarding message:')
        logger.logText('discarding message because %s'%reason)
        return reason
        
    
    def getMailingAddress(self, toinfo):
        if toinfo is None:
            return None
        plusstuff=toinfo.rsplit('+',1)
        if len(plusstuff)<2:
            return None
        remainder=plusstuff[1]
        parts=remainder.split('@')
        if len(parts)<2:
            return None
        tag=parts[0]
        try:
            return DB.MailingList.objects.get(listname__iexact=tag)
        except DB.MailingList.DoesNotExist:
            return None
        except Exception, e:
            logger.logText('***mailing thread exception***')
            logger.handleException(e)
            
    def getBody(self, item):
        body=None
        if item.is_multipart():
            wholebody=str(item.get_payload()[0].get_payload())
        else:
            wholebody=str(item.get_payload())
        #body=self.stripheader(wholebody)
        wholebody=self.stripFooters(wholebody)
        return wholebody 
        
    def stripFooters(self, body):
        # remove the footer
        footer = re.compile(r'\.{60}.*?:{60}', re.DOTALL)
        stripped = footer.sub('',body)
        
        # remove trailing lines that have nothing but blanks and > characters
        trailing = re.compile(r'[>\s]*\Z', re.DOTALL)
        stripped = trailing.sub('',stripped)
        
        return stripped
        
    def getProjectOrTeam(self, mlist, context):
        if mlist.project is None:
            return context
        if mlist.team is None:
            projects=getProjectsInContext(context)
            for project in projects:
                if mlist.project.name==project.title:
                    return project
            return context
        for team in getTeamsInContext(context):
            if team.title==mlist.team.name:
                return team
        return context
    
    
    def rejectedReply(self, sent, mailinglist):
        if sent.subject.lower().find("out of office")>-1:
            return True
        if sent.subject.lower().find("out of the office")>-1:
            return True
        
        if (sent.subject.lower().find("auto")>-1 and 
            sent.subject.lower().find("reply")>-1):
            return True
        if (sent.subject.lower().find("auto")>-1 and 
            sent.subject.lower().find("response")>-1):
            return True
        if (sent.subject.lower().find("delivery")>-1 and 
            (sent.subject.lower().find("error")>-1 or
            sent.subject.lower().find("failure")>-1)):
            return True
        if not mailinglist.replyable:
            #now we check for the project manager being present
            if sent.subject.lower().startswith('re:') or sent.subject.lower().startswith('re '):
                return True
        return False

    def extractEmailAndName(self, emailstring):
        justemail="^[A-Za-z][A-Za-z0-9_.-]*@"+\
            "[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)+$"
        if re.match(justemail, emailstring):
            return emailstring, emailstring
        bracketemail="^<([A-Za-z][A-Za-z0-9_.-]*"+\
            "@[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)+)>$"
        match=re.match(bracketemail,emailstring)
        if match:
            group=match.group(1)
            return group, group
        nameandemail='^"([()a-zA-Z0-9 \'\.-]+)" *'+\
            '<([A-Za-z][A-Za-z0-9_.-]*@'+\
            '[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)+)>$'
        match=re.match(nameandemail, emailstring)
        if match:
            return match.group(1), match.group(2)
        noquotes='^([()a-zA-Z0-9 \'\.-]+) *'+\
            '<([A-Za-z][A-Za-z0-9_.-]*@'+\
            '[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)+)>$'
        match=re.match(noquotes, emailstring)
        if match:
            return match.group(1), match.group(2)    
        
        return False
