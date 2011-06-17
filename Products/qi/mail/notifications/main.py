from datetime import datetime, timedelta
from time import sleep
import transaction

class UpdateProcess(object):
    notificationtime=timedelta(1)
    def __init__(self,app, target):
        self.app=app()
        self.target=target
    def processUpdates(self):
        self.getContext()
        while self.connectionAvailable():
            catalog=self.context.portal_catalog
            brains=catalog.unrestrictedSearchResults(meta_type="qiforum")
            for brain in brains:
                if brain['lastemail'] and brain['lastpost']:
                    if datetime.now()-brain['lastemail']>self.notificationtime and brain['lastemail']<brain['lastpost']:
                        self.sendinfo(brain)
                    else:
                        pass
                else:
                    ob=self.context.unrestrictedTraverse(brain.getPath(), None)
                    if ob is None:
                        pass
                        #TODO: tell the pretty nice portal_catalog that this object is deleted
                        #for now a performance hit every N timeunits seems reasonable
                    else:
                        ob.lastemail=getattr(ob, 'lastemail', datetime.now())
                        if getattr(ob, 'lastpost', None):
                            catalog.reindexObject(ob)
                            transaction.get().commit()
                        else:
                            pass
            transaction.get().commit()
            sleep(2000)
            
    
    def sendinfo(self, brain):
        sentfor=brain.getObject()
        sent=[]
        print sentfor.subscribers
        for subscriber in sentfor.subscribers:
            atool = self.context.acl_users
            try:
                user=atool.getUserById(subscriber)
            except:#any failure to lookup said user
                continue#I hate gotos but this is as good a solution as I can come up with
            if user.has_permission('View',sentfor):
                sent.append(subscriber)
        self.dosend(sentfor,sent)
    
    def dosend(self, ob, recipients): 
        posts=ob.recentposts(ob.lastemail)
        if len(posts)==0:
            #reindex last email
            self.context.portal_catalog.reindexObject(ob)
            return
        if len(recipients)==0:
            return
        
        header="""Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
To: 'Forum Subscibers'
From: 'QI TeamSpace Forum Subscribers'


"""
        lead="""You are receiving this message because you subscribed to %(obname)s. 
This is the daily update of the changes on %(obname)s.
If you don't wish to wish to recieve these updates please go to %(url)s/unsubscribe (you may have to log in).
"""%{'obname':ob.title, 'url':ob.absolute_url()}
        message=u'\n----------\n'.join([post.body for post in posts])
        message=header+lead+message
        result=self.mailer.send(str(message), recipients, 'forumupdates@qiteamspace.com')
        ob.lastemail=datetime.now()
        ob._p_changed=1
    def connectionAvailable(self):
        return self.context is not None
    def getContext(self):
        self.context=getattr(self.app, self.target, None)
        self.mailer=self.context.MailHost

if __name__=="__main__":
    try:
        # Zope 2.8 on, Zope is now 'Zope2' and 'zope' is the Zope 3
        # libs.
        import Zope2 as Zope
    except ImportError:
        import Zope
    #grab our zope config file
    configfile = _args[1]

    sys.argv=sys.argv[:1]#this is needed for some idiotic reason

    Zope.configure(configfile)
    run=UpdateProcess(Zope.app,'qiteamspace')
    
    run.processUpdates()
    
