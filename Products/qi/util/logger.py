from datetime import datetime
import sys
import traceback
from django.db import connection

class LogHandler:
    target="log/qiteamspace.log"
    globalerror=open('log/errorlist.log','a')
    def bootup(self):
        self.lasttime=datetime.now()
        self.out=open(self.target,'a')
    def logText(self, text):
        self.out.write(str(datetime.now())+":  "+str(text)+'\n')
        self.out.flush()
    def logException(self, exceptionparts, trace):
        basemessage='\nException occured at %s\n'
        self.out.write(basemessage%datetime.now())
        self.out.write('=======================\n')
        traceback.print_tb(trace,None, self.out)
        if hasattr(exceptionparts,'args'):
            for part in exceptionparts:
                try:
                    self.out.write( (u' \n'+unicode(str(part),'utf-8')+u'\n').encode('utf-8') )
                except (UnicodeDecodeError, UnicodeEncodeError):
                    self.out.write( ' \n'+str(part)+'\n')
                except:
                    self.out.write('problem trying to print something'+str(type(part)))
        self.out.write('=======================\n')
        self.out.flush()

    
    def resetTime(self):
        self.lasttime=datetime.now()
    
    def logWithElapsed(self, message):
        elapsed=datetime.now()-self.lasttime
        self.lasttime=datetime.now()
        self.logText('%s %s'%(elapsed,message))
    
    def handleException(self,e, view=None):
        try:
            x,y,trace=sys.exc_info()
            if view is not None:
                self.logText('view was %s'%view)
            self.globalerror.write(str(datetime.now())+": "+self.target)
            self.logText('x: %s, y:%s'%(str(x),str(y)))
            self.logException(e,trace)
            self.logText('resetting transaction')
            connection._rollback()
        except:
            try:
                self.logText('unhandlable exception')
            except:
                pass

logger=LogHandler()
logger.bootup()

actionlog=LogHandler()
actionlog.target="log/actions.log"
actionlog.bootup()

maillog=LogHandler()
maillog.target="log/mailinglist.log"
maillog.bootup()

importlog=LogHandler()
importlog.target="log/import.log"
importlog.bootup()

projectlog=LogHandler()
projectlog.target="log/projects.log"
projectlog.bootup()