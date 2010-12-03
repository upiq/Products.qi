from Products.qi.util.general import BrowserPlusView
from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName

try: 
    # Plone 4 and higher 
    import plone.app.upgrade 
    PLONE_VERSION = 4 
except ImportError: 
    PLONE_VERSION = 3


class ContactView(BrowserPlusView):
    processFormButtons=('form.button.Send',)
    def fakeportal(self):
        return self.context.getProject()
        
    def validate(self, form):
        if not self.getProjectEmail():
            self.addError('base','This project has no managers')
        self.required('subject')
        self.required('message')
        form=self.context.request.form
        code_generated = self.context.portal_captcha.getGeneratedCaptchaCode(form['hidden_captcha_code'])
        if code_generated!=form['code_entered_by_user']:
            self.addError('captcha','Please enter the code from the image on the left')
        
    def action(self, action, form):
        subject = self.context.REQUEST.get('subject', '')
        message = self.context.REQUEST.get('message', '')
        sender_from_address = self.context.REQUEST.get('sender_from_address', '')
        sender_fullname = self.context.REQUEST.get('sender_fullname', '')
        
        if not sender_from_address or sender_from_address=='':
            securityMan=getSecurityManager()
            user=securityMan.getUser()
            if str(user)=='admin':
                sender_fullname='QI Teamspace Administrator'
                sender_from_address='admin@qiteamspace.com'
            else:
                mtool = getToolByName(self.context, 'portal_membership')
                print mtool.getMemberInfo(user)
        else:
            pass
            
        
        send_to_address = self.getProjectEmail()
        envelope_from = self.getProjectEmail()
        
        
        host = self.context.MailHost # plone_utils.getMailHost() (is private)
        encoding = "us-ascii"
        
        variables = {'sender_from_address' : sender_from_address,
                     'sender_fullname'     : sender_fullname,             
                     'url'            : self.context.getProject().absolute_url(),
                     'subject'        : subject,
                     'message'        : message
                     }
        
        try:
            message = self.context.site_feedback_template(self.context,
                    **variables)
            if PLONE_VERSION==3:
                result = host.secureSend(message, send_to_address, envelope_from,
                    subject=subject, subtype='plain', charset=encoding,
                    debug=False, From=sender_from_address)
            else:
                #Plone4 removes SecureMailHost; instead use stock setup with
                #   Zope mailhost, zope.sendmail
                result = host.send(message, send_to_address, envelope_from,
                          subject=subject, encode=None) #encode 7bit default
                                                                                
        except:
            raise
            
        self.doRedirect()
            
            
    def getProjectEmail(self):
        if hasattr(self.context, 'ProjectEmail'):
            return self.context.ProjectEmail
        else:
            possibleManagers=self.context.getProjectUsers('managers')
            if(len(possibleManagers)>0):
                return possibleManagers[0]
            else: 
                return None
            
            
            
