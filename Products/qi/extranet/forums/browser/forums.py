from Products.qi.util.general import BrowserPlusView
from plone.app.form import base
from Products.qi.extranet.forums.interfaces import IForum, IThread, IPost
from Products.qi.extranet.forums.content import threadFactory
from plone.app.form import base
from zope.component import createObject
from zope.formlib import form
from Products.qi import MessageFactory as _
from datetime import datetime
import OFS.Image
import string as stringlib
from Products.Five.browser import BrowserView

from Products.CMFDefault.File import File

class ForumView(BrowserPlusView):
    removeBorders=False
    def allowssubforums(self):
        mtool = self.context.portal_membership
        return mtool.checkPermission("Manage Site",self.context)
    def allowsthreads(self):
        mtool = self.context.portal_membership
        return mtool.checkPermission("Post Threads",self.context)
class ThreadView(BrowserPlusView):
    def allowsreplies(self):
        mtool = self.context.portal_membership
        return mtool.checkPermission("Post Threads",self.context)

forum_form_fields = form.Fields(IForum)

class AddForum(base.AddForm):#make this an adding view
    form_fields = forum_form_fields
    label = _(u"Add Forum")
    form_name = _(u"Forum Settings")
    
    def setUpWidgets(self, ignore_request=False):

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)
    

    
    def create(self, data):
        chart = createObject(u"qi.Forum")
        form.applyChanges(chart, self.form_fields, data)
        return chart

thread_form_fields = form.Fields(IThread)
class AddThread(base.AddForm):#make this an adding view
    form_fields = thread_form_fields
    label = _(u"Add Forum")
    form_name = _(u"Forum Settings")

    def setUpWidgets(self, ignore_request=False):

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)

    def create(self, data):
        thread = createObject(u"qi.Thread")
        form.applyChanges(thread, self.form_fields, data)
        return thread

def makeid(string):
    newstring=''.join([x for x in string if x in stringlib.ascii_letters+' '])
    result= '-'.join(newstring.split())
    if len(result)==0:
        return "untitled-%i"%hash(string)
    return result

class PostThread(BrowserPlusView):
    processFormButtons=("post",)
    def validate(self, form):
        self.required('threadtitle',"Post Title")
            
        self.required('postbody',"Post Text")
    def action(self, form, action):
        added=threadFactory()
        title=form['threadtitle']
        added.id=makeid(title)
        added.title=title
        added.dateadded=datetime.now()
        added.owner=self.user()
        
        self.context._setObject(added.id, added)
        firstpost=added.post(form['postbody'])
        firstpost.owner=self.user()
        thread=getattr(self.context,added.id)
        thread._setObject(firstpost.id,firstpost )
        self.context.orderObjects('dateadded')
        self.request.response.redirect(thread.absolute_url())
        
        if 'attachment' in form:
            attachments=form['attachment']
            if not isinstance(attachments, list):
                attachments=[attachments]
        else:
            attachments=[]
            
        newlyadded=getattr(thread,firstpost.id)
        for attached in attachments:
            if attached is not None:
                content= attached.headers.dict['content-type']
                id, title = OFS.Image.cookId(None, None, attached)
                attachedobject=File( id=id, title=title,file=attached, content_type=content)
                attachedobject.portal_type="File"
                attachedobject.creators=(unicode(self.user()),)
                newlyadded._setObject(attachedobject.id,attachedobject)
        self.context.updateforum(datetime.now())
        #self.context.updatethread(datetime.now())
        catalog=self.context.portal_catalog
        parent=self.context.aq_inner.aq_parent
        catalog.reindexObject(self.context)
        catalog.reindexObject(parent)

class Reply(BrowserPlusView):
    processFormButtons=("post",)
    def validate(self, form):
        self.required("postbody","Post Text")
    def action(self, form, action):
        post=self.context.post(form['postbody'])
        #get files
        if 'attachment' in form:
            attachments=form['attachment']
            if not isinstance(attachments, list):
                attachments=[attachments]
        else:
            attachments=[]
        self.context._setObject(post.id, post)
        self.context.orderObjects('dateadded')
        self.request.response.redirect('%s#last'%self.context.absolute_url())
        newlyadded=getattr(self.context,post.id)
        for attached in attachments:
            if attached and attached.filename:
                content= attached.headers.dict['content-type']
                id, title = OFS.Image.cookId(None, None, attached)
                attachedobject=File( id=id, title=title,file=attached, content_type=content)
                attachedobject.portal_type="File"
                newlyadded._setObject(attachedobject.id,attachedobject)
        

class Subscribe(BrowserPlusView):
    def __call__(self, *args, **kw):
        self.context._subscribe(self.user())
        self.doRedirect("view")
class UnSubscribe(BrowserPlusView):
    def __call__(self, *args, **kw):
        self.context._unsubscribe(self.user())
        self.doRedirect("view")

class DeletePost(BrowserPlusView):
    def __call__(self):
        deleted=self.context
        thread=deleted.getThread()
        thread._delOb(deleted.id)
        #deleted.DELETE(self.request, self.request.response)
        thread._objects = tuple([info for info in thread._objects
                              if info['id']!=(deleted.id)])
        thread._p_changed=1
        self.request.response.redirect(thread.absolute_url())

class EditPost(BrowserPlusView):
    processFormButtons=("edit",)
    def validate(self, form):
        pass
    def action(self, form, action):
        post=self.context
        #get files
        if 'attachment' in form:
            attachments=form['attachment']
            if not isinstance(attachments, list):
                attachments=[attachments]
        else:
            attachments=[]
        self.request.response.redirect('%s#last'%self.context.getThread().absolute_url())
        newlyadded=post
        post.body=form['postbody']
        post._p_changed=1
        for attached in attachments:
            if attached and attached.filename:
                content= attached.headers.dict['content-type']
                id, title = OFS.Image.cookId(None, None, attached)
                attachedobject=File( id=id, title=title,file=attached, content_type=content)
                attachedobject.portal_type="File"
                attachedobject.creators=(unicode(self.user()),)
                newlyadded._setObject(attachedobject.id,attachedobject)
    