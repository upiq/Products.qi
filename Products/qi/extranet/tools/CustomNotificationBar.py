from Globals import Persistent
from App.special_dtml import DTMLFile
import Acquisition
import OFS.SimpleItem
from AccessControl.Role import RoleManager

from AccessControl import ClassSecurityInfo
from zope.interface import Interface,implements
from Products.CMFCore.utils import registerToolInterface
from App.class_init import default__class_init__ as InitializeClass

class INotificationBar(Interface):
    pass
    
registerToolInterface("Notification bar",INotificationBar)

class CustomNotificationBar(Persistent, Acquisition.Implicit, OFS.SimpleItem.Item, RoleManager):
    implements(INotificationBar)
    meta_type="custom notification"
    manage=manage_main= DTMLFile("CustomBar",globals())
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
    
    def __init__(self, id='', title='', headline='',
                 rawhtml=''):
        self.id=id
        self.setConfig(title, headline, rawhtml)
    
    security.declareProtected("Change Configuration","manage_makeChanges")
    def manage_makeChanges(self, title, headline, rawhtml,REQUEST=None,source_domain='qiteamspace.com',
                            bounce_addr='bounced@ursalogic.com',
                            name_part="mailinglist"):
        """make the changes"""
        self.setConfig(title,headline,rawhtml)
        if REQUEST is not None:
            msg = 'message bar %s updated' % self.id
            return self.manage_main(self, REQUEST, manage_tabs_message=msg)
    security.declarePrivate('setConfig')
    def setConfig(self, title, headline, rawhtml):
        self.title=title
        self.headline=headline
        self.rawhtml=rawhtml
