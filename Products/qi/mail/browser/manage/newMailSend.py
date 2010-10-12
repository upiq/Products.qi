from Products.qi.util.general import BrowserPlusView
from Products.qi.mail.newlist import Message
from Products.CMFCore.utils import getToolByName
from qi.sqladmin import models as DB
#from DateTime.DateTime import datetime
import AccessControl
from Products.qi.util import utils
from Products.qi.extranet.pages.success import Success
from time import sleep
        
        
class SetupGroups(BrowserPlusView):
    processFormButtons=('add',)
    def validate(self, form):
        self.required('added')
    def action(self, form, action):
        added=DB.SpecialMailGroup()
        added.groupname=form['added']
        added.save()
    