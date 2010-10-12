from zope.interface import Interface
from zope import schema
from Products.qi import MessageFactory as _

class IForum(Interface):
    title=schema.TextLine(title=_(u"Title"),
                        description=_("Name of this forum"),
                        required=True)
    description=schema.Text(title=_(u"Description"),
                            description=_(u"Description of the topics discussed on this forum."),
                            required=True)

class IThread(Interface):
    def most_recent_post(self):
        """Used for ordering threads in the forum"""
    title=schema.TextLine(title=_(u"Title"),
                        description=_(""),
                        required=True)
    body=schema.Text(title=_(u"Body"),
                            description=_(u""),
                            required=True)


class IPost(Interface):
    def get_attachments(self):
        pass
    body=schema.Text(title=_(u"Body"),
                            description=_(u"Type the contents of your reply here"),
                            required=True)
class ISubscribable(Interface):
    def _subscribe(self,user):
        """Assigns a user to the object to recieve updates"""
    def _unsubscribe(self, user):
        """removes a user from an obect recieving updates"""