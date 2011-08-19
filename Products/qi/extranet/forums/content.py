from interfaces import IForum, IThread, IPost, ISubscribable
from plone.app.content.container import Container
from zope.component.factory import Factory
from Products.qi import MessageFactory as _
from App.class_init import default__class_init__ as InitializeClass
from zope.interface import implements
from plone.app.content.interfaces import INameFromTitle
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from datetime import datetime
from Acquisition import aq_self
from Products.CMFDefault.interfaces import IFile


class Forum(Container,BrowserDefaultMixin):
    portal_type="qi.Forum"
    subscribers=set()
    implements(IForum,INameFromTitle, ISubscribable)
    lastemail=None
    def __init__(self):
        self.lastemail=datetime.now()
        self.subscribers=set()
    def updateMetadata(self):
        #do NOT reverse the order of these ifs
        if not getattr(self, 'lastpost',None):
            self.lastpost=datetime.now()
        if not getattr(self, 'lastemail',None):
            self.lastemail=datetime.now()
            #it's important that if we lack data, we don't spam our users 
            #with more info than they'd want
    def recentposts(self, sincewhen):
        posts=[]
        for thread in self.threads():
            posts.extend(thread.recentposts(sincewhen))
        return posts
    
    def getForum(self):
        return self

    def subforums(self):
        result=[x for x in self.getChildNodes() if IForum.isImplementedBy(x)]
        return result
    def threads(self):
        result=[x for x in self.getChildNodes() if IThread.isImplementedBy(x)]
        return result
    def updateforum(self,posttime):
        self.lastpost=posttime
        if not getattr(self, 'lastemail',None):
            self.lastemail=datetime.now()
    def _subscribe(self, user):
        self.subscribers.add(user)
        self._p_changed=True
    def _unsubscribe(self, user):
        self.subscribers.remove(user)
        self._p_changed=True
        
    
    
    
class Thread(Container):
    portal_type="qi.Thread"
    implements(IThread, ISubscribable)
    body=""
    title=""
    subscribers=set()
        
    def post(self, body):
        
        created=postFactory()
        created.body=body.replace('\n','<br />')
        created.posted=datetime.now()
        pieces=body.strip().split()
        if len(pieces)>3:
            idval='-'.join(pieces[:3])
            titleval=' '.join(pieces[:3])
        else:
            idval='-'.join(pieces)
            titleval=' '.join(pieces)
        realid=""
        for s in idval:
            if s.isalnum() or s=='-':
                realid+=s
        created.id=realid or "empty"
        created.title=titleval
        self.lastpost=created.posted
        return created
    def getThread(self):
        return self
    def mostrecentpost(self):
        return self.getLastChild()
    def recentposts(self, sincewhen):
        result=[]
        for x in self.getChildNodes():
            try:
                t=x.modification_date
                mod=datetime(t.year(),t.month(),t.day(),t.hour(),t.minute(), t.second())
                if IPost.isImplementedBy(x) and mod>sincewhen:
                    result.append(x)
                else:
                    pass
            except TypeError:
                print 'exception', x, x.modification_date
        return result
    def posts(self):
        result=[x for x in self.getChildNodes() if IPost.isImplementedBy(x)]
        return result
    def __init__(self,*args,**kw):
        self.subscribers=set()
        self.date=datetime.now()
    def _subscribe(self, user):
        self.subscribers.add(user)
        import transaction
    def _unsubscribe(self, user):
        self.subscribers.remove(user)


class Post(Container):#needs to contain attachments
    portal_type="qi.Post"
    implements(IPost)
    def canedit(self):
        mtool = self.portal_membership
        return mtool.checkPermission("Modify Portal Content",self)
    def attachments(self):
        result=[x for x in self.getChildNodes() if IFile.isImplementedBy(x)]
        return result
    def getOwnerName(self):
        mtool = getToolByName(self, 'portal_membership')
        return mtool.getMemberInfo(self.owner)['fullname']
    
InitializeClass(Forum)
forumFactory = Factory(Forum, title=_(u"Create a document discussion forum"))
threadFactory =  Factory(Thread, title=_(u"Post a new thread"))
postFactory = Factory(Post, title=_(u"Post a reply"))
