from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility
#from mailbuilder import buildMail


"""def sendSomethin(address,context):
    host = getUtility(IMailHost)
    buildMail(context)
    """

class MailBatch:
    messages=None
    def prepare(self,message, mailinglist, subject, context,
                fromaddr,owner=None):
        if owner is None:
            owner=context
        self.messages= [buildMail(message, address,subject, context,
            fromaddr,owner=owner) for address in mailinglist]
    
    def sendMessages(self,utility=None):
        if not self.messages:
            raise AttributeError(\
                'messages were not prepared prior to being used')
        if utility:
            host=utility
        else: 
            host=getUtility(IMailHost)
        for message in self.messages:
            host.send( message)