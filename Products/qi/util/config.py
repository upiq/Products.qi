from App.config import getConfiguration


# global, cached state for loaded configuration
_prod_cfg = {}
_prod_cfg_locked = False


def loadcfg():
    """Load product configuration; changes require Zope instance restart"""
    #import pdb; pdb.set_trace()
    global _prod_cfg
    global _prod_cfg_locked
    if _prod_cfg:
        return _prod_cfg #naively return cached, already loaded.
    cfg = getConfiguration()
    if hasattr(cfg, 'product_config'):
        prodcfg = cfg.product_config.get('qi', {})
        if not prodcfg:
            return
        while _prod_cfg_locked:
            pass #wait to acquire lock, avoid race-condition.
        _prod_cfg_locked = True
        _prod_cfg = prodcfg
        _prod_cfg_locked = False


def getcfg():
    if not _prod_cfg:
        loadcfg()
    return _prod_cfg


class PathConfig(object):
    """
    get a configured path by name (prefixed with paths.") from Product
    configuration.  This class implements a filtered mapping proxy interface
    to present a subset of all configuration key/value pairs.

    One can load configuration in zope.conf like this:
        <product-config qi>
            paths.buildout  /path/to/some/build/of/qiteamspace
            paths.src       /path/to/some/build/of/qiteamspace/src
        </product-config>
    
    Or this can be included in instance configuration in buildouts using the
    plone.recipe.zope2instance recipe:
    
        [paths]
        checkout = ${buildout:directory}/parts/qit_checkout/qit
        
        [instance]
        recipe = plone.recipe.zope2instance
        #... options here ...
        zope-conf-additional = 
        <product-config qi>
            paths.buildout  ${buildout:directory}
            paths.checkout  ${paths:checkout}
        </product-config>

    Note: while the path names are qualified in configuration with the prefix
    "paths.", keys in PathConfig have this namespace removed.
    """
    
    def __init__(self):
        loadcfg() #boostrap cached global config
    
    def _cfgkey(self, name):
        return 'paths.%s' % name
    
    def __getitem__(self, name):
        return _prod_cfg.__getitem__(self._cfgkey(name))
    
    def __contains__(self, name):
        return _prod_cfg.__contains__(self._cfgkey(name))
    
    def get(self, name, default=None):
        return _prod_cfg.get(self._cfgkey(name), default)
    
    def keys(self):
        """filtered names, shortened: e.g. 'sql' <--> 'paths.sql' """
        return [k[6:] for k in _prod_cfg if k.startswith('paths')]

    def values(self):
        return [self.get(k) for k in self.keys()]
    
    def items(self):
        return [(k,self.get(k)) for k in self.keys()]
    
    def __iter__(self):
        return self.keys.__iter__()

