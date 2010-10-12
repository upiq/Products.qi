from Products.CMFCore.utils import getToolByName
from Products.qi.util.utils import get_factory_permission
from Products.qi.extranet.types.interfaces import _PROJECT_LOGO_NAME
from zExceptions import BadRequest
from threading import Semaphore
from Products.qi.mail.newListener import MailListener, imapEnabled
from threading import currentThread
from Products.qi.datacapture.file.uploads import UploadThread
from Products.qi.util.logger import logger




mailThread=None
lock=Semaphore()
uploadThread=None

def bootup(someObject,someEvent):
    lock.acquire()
    try:
        global mailThread
        global uploadThread
        if imapEnabled(someObject):
            if mailThread is None or not mailThread.isAlive():
                mailThread=MailListener()
                mailThread.owner=currentThread()
                mailThread.context=someObject
                mailThread.start()
        if uploadThread is None or not uploadThread.isAlive():
            uploadThread=UploadThread.UploadListener()
            uploadThread.start()
    except Exception, e:
        logger.handleException(e)
        pass
    lock.release()

