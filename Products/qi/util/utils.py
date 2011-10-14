from Products.CMFCore.utils import getToolByName 

from Products.qi.extranet.types import project, team


def find_parents(context, typename=None, findone=False, start_depth=2):
    if findone and typename is None:
        parent = getattr(context, '__parent__', None)
        if parent:
            return parent #immediate parent of context
    result = []
    catalog = getToolByName(context, 'portal_catalog')
    path = context.getPhysicalPath()
    for subpath in [path[0:i] for i in range(len(path)+1)][start_depth:]:
        query = {
            'path' : { 
                'query' : '/'.join(subpath),
                'depth' : 0,
                },
            'Type' : typename,
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
        return None # never found one
    return result


def find_parent(context, typename=None, start_depth=2):
    return find_parents(context, typename, findone=True, start_depth=start_depth)


def project_containing(context):
    return find_parent(context, typename='QI Project')


def team_containing(context):
    return find_parent(context, typename='QI Team', start_depth=3)


def getProjectsInContext(context):
    catalog = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath())
    query = {
        'path' : {
            'query' : path,
            'depth' : 2
            },
        'Type' : 'QI Project',
        }
    return [b._unrestrictedGetObject() for b in catalog.search(query)]


def getTeamsInContext(context):
    catalog = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath())
    query = {
        'path' : {
            'query' : path,
            'depth' : 2
            },
        'Type' : 'QI Team',
        }
    return [b._unrestrictedGetObject() for b in catalog.search(query)]

