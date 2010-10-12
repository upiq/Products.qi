from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory('Products.qi')

#from Products.qi.util.auth import whoplugin
import os
from django.conf import settings
#import qi.sqladmin.settings
from Products.PluggableAuthService.PluggableAuthService import \
     registerMultiPlugin
#registerMultiPlugin(whoplugin.WhoPlugin.meta_type)
os.environ['DJANGO_SETTINGS_MODULE']='qi.sqladmin.settings'

def initialize(context):
    """ Initialize the product """
    pass
    """
    from AccessControl.Permissions import manage_users
    context.registerClass(whoplugin.WhoPlugin,
                          permission = manage_users,
                          constructors = (whoplugin.manage_addWhoPluginForm,
                                          whoplugin.manage_addWhoPlugin,),
                          visibility=None)
    
    #try registering all projects with the database?"""
    