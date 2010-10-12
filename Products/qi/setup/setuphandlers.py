import re

def setupRDBConnection(context, **kw):
    """ Set up a relational database connecton in the root (brutally) """
    site = context.getSite()
    addConn = site.manage_addProduct['ZPsycopgDA'].manage_addZPsycopgConnection
    if not hasattr(site, 'rdb_connection'):
        addConn('rdb_connection', 'Postgres Connection',
                'host=localhost port=5055 dbname=qiteamspace')