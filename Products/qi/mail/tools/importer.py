
from Products.MailHost.interfaces import IMailHost
from Products.qi.mail.tools.imaphost import IIMAP
import xml.dom.minidom as XML

from zope.component import getSiteManager

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

def importMailHost(context):
    """Import mailhost settings from an XML file.
    """
    print 'importMailHost'
    try:
        sm = getSiteManager(context.getSite())
        tool = sm.getUtility(IIMAP)
        k=context.readDataFile('imaphost.xml')
        v=XML.parseString(k)
        o=v.firstChild
        tool.imap_host=o.getAttribute('imap_host')
        tool.imap_port=o.getAttribute('imap_port')
        tool.imap_pass=o.getAttribute('imap_pass')
        tool.imap_userid=o.getAttribute('imap_userid')
        importObjects(tool, '', context)
    except TypeError, e:
        #do nothing
        pass
