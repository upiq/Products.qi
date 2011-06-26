from App.config import getConfiguration
from ZODB import DB as ZopeDB

def new_approot():
    """
    Get a new application root with a distinct ZODB connection.  This
    should be saved in a thread-local storage on a new thread, and
    reference to returned application root should be deleted prior
    to closing connection.
    
    Returns two-item tuple of connection, application root.
    """
    config = getConfiguration()
    maindb = [zdb for zdb in config.databases if zdb.getName() == 'main'][0]
    dbconf = maindb.config
    storage = dbconf.storage.open()
    db = ZopeDB(storage)
    conn = db.open()
    return (conn, conn.root()['Application'])

