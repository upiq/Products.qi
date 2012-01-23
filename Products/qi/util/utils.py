from zope.interface import implements
from Products.CMFCore.utils import getToolByName


from Products.qi.extranet.types import project, team
from Products.qi.extranet.types.interfaces import IWorkspaceContext


def find_parents(context, typename=None, findone=False, start_depth=2):
    if findone and typename is None:
        parent = getattr(context, '__parent__', None)
        if parent:
            return parent   # immediate parent of context
    result = []
    catalog = getToolByName(context, 'portal_catalog')
    path = context.getPhysicalPath()
    for subpath in [path[0:i] for i in range(len(path) + 1)][start_depth:]:
        query = {
            'path': {
                'query': '/'.join(subpath),
                'depth': 0,
                },
            'Type': typename,
            }
        if typename is None:
            del(query['Type'])
        brains = catalog.search(query)
        if not brains:
            continue
        else:
            item = brains[0]._unrestrictedGetObject()
            if findone:
                return item
            result.append(item)
    if findone:
        return None     # never found one
    return result


def find_parent(context, typename=None, start_depth=2):
    return find_parents(
        context,
        typename,
        findone=True,
        start_depth=start_depth,
        )


def project_containing(context):
    return find_parent(context, typename='QI Project')


def team_containing(context):
    return find_parent(context, typename='QI Team', start_depth=3)


def getProjectsInContext(context):
    catalog = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath())
    query = {
        'path': {
            'query': path,
            'depth': 2
            },
        'Type': 'QI Project',
        }
    return [b._unrestrictedGetObject() for b in catalog.search(query)]


def getTeamsInContext(context):
    catalog = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath())
    query = {
        'path': {
            'query': path,
            'depth': 2
            },
        'Type': 'QI Team',
        }
    return [b._unrestrictedGetObject() for b in catalog.search(query)]


class WorkspaceUtilityView(object):
    """
    Workspace utility view: view or adapter for content context in
    a Plone site to get team or project workspace context.
    """
    
    implements(IWorkspaceContext)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
    
    def __call__(self, *args, **kwargs):
        content = "Workspace utility view"
        response = self.request.response
        response.setHeader('Content-type', 'text/plain')
        response.setHeader('Content-Length', len(content))
        return content
    
    def team(self):
        """get team containing or None"""
        return team_containing(self.context)        # may be None
    
    def project(self):
        """get project containing or None"""
        return project_containing(self.context)     # may be None
    
    def workspace(self):
        """
        get most immediate workspace team or project 
        containing or None
        """
        return self.team() or self.project()        # may be None

