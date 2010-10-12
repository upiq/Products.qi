from zope.interface import implementer

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName

@implementer(IVocabularyFactory)
def globally_allowed_types(context):
    context = getattr(context, 'context', context)
    portal_types = getToolByName(context, 'portal_types')
    items = []
    for fti in portal_types.listTypeInfo():
        if getattr(fti, 'globalAllow', lambda: False)() == True and fti.title:
            items.append((fti.title, fti.getId(),))
    return SimpleVocabulary.fromItems(items)

_USER_PLUGIN_IDS = ['source_users']

@implementer(IVocabularyFactory)
def all_users(context):
    context = getattr(context, 'context', context)
    acl_users = getToolByName(context, 'acl_users')
    users = acl_users.searchUsers(sort_by='login')
    items = [ (x['userid'], x['login']) for x in users if x['pluginid']
              in _USER_PLUGIN_IDS ]
    return SimpleVocabulary.fromItems(items)

@implementer(IVocabularyFactory)
def getUploadableTypes(context):
    context=getattr(context,'context',context)
    project=context.aq_inner
    items=[(v.getName(),v.getName()) for v in project.getUploadTypes()]
    return SimpleVocabulary.fromItems(items)

@implementer(IVocabularyFactory)
def public_skins(context):
    skins=context.portal_skins
    return SimpleVocabulary.fromItems([(x,x) for x in skins.getSkinSelections()])
    
