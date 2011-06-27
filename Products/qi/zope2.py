
def initialize(context):
    """make this package a zope2 product"""
    from Products.qi.util.config import getcfg
    cfg = getcfg()
    if 'sqladmin.port' in cfg:
        # should be 'hostname:tcp_port'
        import os
        os.environ['QI_SQLADMIN_DBPORT'] = cfg['sqladmin.port'].strip()


