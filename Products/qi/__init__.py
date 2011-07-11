import os

from zope.i18nmessageid import MessageFactory

import zope2

MessageFactory = MessageFactory('Products.qi')

# configure QI_SQLADMIN_DBPORT environ variable for
# qi.sqladmin.settings to use as early as possible at 
# start-up; ensures that settings gets correct DB 
# socket (either TCP or unix domain socket -- sourced
# from product config section in zope.conf, and usually
# provided into configuration by a buildout).
zope2.initialize(None)

os.environ['DJANGO_SETTINGS_MODULE'] = 'qi.sqladmin.settings'

