import os

from zope.i18nmessageid import MessageFactory


MessageFactory = MessageFactory('Products.qi')


os.environ['DJANGO_SETTINGS_MODULE'] = 'qi.sqladmin.settings'

