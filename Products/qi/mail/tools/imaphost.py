from Products.MailHost.MailHost import MailHostError, MailBase
from Persistence import Persistent
from App.special_dtml import DTMLFile
import Acquisition
import OFS.SimpleItem
from AccessControl.Role import RoleManager
from email import message_from_string

from AccessControl import ClassSecurityInfo
from zope.interface import Interface,implements
from Products.CMFCore.utils import registerToolInterface
import imaplib

class IIMAP(Interface):

    def getmail(filterer):
        """Send mail.
        """
registerToolInterface('IMAP host', IIMAP)

class IMapHost( Persistent,Acquisition.Implicit,
                OFS.SimpleItem.Item, RoleManager):
    implements(IIMAP)
    manage=manage_main = DTMLFile('IMAPHost', globals())
    meta_type='IMAP Host'
    manage_main._setName('manage_main')
    index_html=None
    
    manage_options=(
        (
        {'icon':'', 'label':'Edit',
         'action':'manage_main',
         'help':('MailHost','Mail-Host_Edit.stx')},
        )
        +RoleManager.manage_options
        +OFS.SimpleItem.Item.manage_options
        )        

    security = ClassSecurityInfo()

    def __init__(self, id='', title='', imap_host='localhost',
                 imap_port=993, imap_userid='', imap_pass='',
                 disabled=True, source_domain='qiteamspace.com',
                 bounce_addr='bounced@ursalogic.com',
                 name_part='mailinglist'):
        """Initialize a new MailHost instance
        """
        self.id = id
        self.setConfiguration(title, imap_host, imap_port,
                              imap_userid, imap_pass, disabled,source_domain,
                              bounce_addr,name_part)

    security.declareProtected('Change configuration', 'manage_makeChanges')
    def manage_makeChanges(self, title, imap_host, imap_port,
                           imap_userid, imap_pass,
                           disabled=False,
                           REQUEST=None,source_domain='qiteamspace.com',
                           bounce_addr='bounced@ursalogic.com',
                           name_part="mailinglist"):
        """Make the changes
        """
        self.setConfiguration(title, imap_host, imap_port,
                              imap_userid, imap_pass,disabled,source_domain,
                              bounce_addr,name_part)
        if REQUEST is not None:
            msg = 'MailHost %s updated' % self.id
            return self.manage_main(self, REQUEST, manage_tabs_message=msg)

    security.declarePrivate('setConfiguration') 
    def setConfiguration(self, title, imap_host, imap_port,
                         imap_userid, imap_pass,disabled,source_domain,
                         bounce_addr,name_part):
        """Set configuration
        """
        self.title = title
        self.imap_host = str(imap_host)
        self.imap_port = int(imap_port)
        if imap_userid:
            self._imap_userid = imap_userid
            self.imap_userid = imap_userid
        else:
            self._imap_userid = ''
            self.imap_userid = ''
        if imap_pass:
            self._imap_pass = imap_pass
            self.imap_pass = imap_pass
        else:
            self._imap_pass = ''
            self.imap_pass = ''
        self.source_domain=source_domain
        self.disabled=disabled
        self.bounce_addr=bounce_addr
        self.name_part=name_part
            
            
    def getNextGroup(self,boxname='INBOX'):
        box=self.boot()
        items=self.retreiveItems(box, boxname,5)
        self.finish(box)
        return items
        
    def boot(self):
        box=imaplib.IMAP4_SSL(self.imap_host,int(self.imap_port))
        box.login(self.imap_userid,self.imap_pass)
        return box
    def retreiveItems(self,box,boxname,maxcount):
        box.select(boxname)
        stuff, data=box.search(None,'ALL')
        if data[0]=='':
            return []
        keys=data[0].split(' ')
        if len(keys)>maxcount:
            keys=keys[0:maxcount]
        result=[]
        
        for key in keys:
            nonsense, mail=box.fetch(key,'(RFC822)')
            data=mail[0]
            message=data[1]
            result.append(message_from_string(message))
            #flag it for deletion, will be deleted when box is closed
            box.store(key, '+FLAGS', '\\Deleted')
            
        
        box.close()
        return result
    
    def finish(self,box):
        box.logout()
        

    
