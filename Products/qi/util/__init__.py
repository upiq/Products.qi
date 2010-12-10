
# Plone version checker:
# usage: >>> from Products.qi.util import PLONE_VERSION
try:
    # Plone 4 and higher 
    import plone.app.upgrade
    PLONE_VERSION = 4
except ImportError:
    PLONE_VERSION = 3

