from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.criteria.portaltype import ATPortalTypeCriterion
from Products.ATContentTypes.criteria.relativepath import ATRelativePathCriterion
from Products.ATContentTypes.criteria.sort import ATSortCriterion
from datetime import datetime
def AddFileCollection(context,event):
    added=ATTopic("files")
    added.portal_type="Topic"
    added.id="files"
    added.title="All uploaded files"
    added.customView=True
    added.customViewFields=(u'Title', u'getObjSize', u'ModificationDate', u'Creator')
    context._setObject("files",added)
    subcontext=getattr(context,"files")
    wftool = subcontext._getWorkflowTool()
    wftool.doActionFor(subcontext, 'publish')
    a=getFileRestriction()
    subcontext._setObject("crit__Type_ATPortalTypeCriterion", a)
    b=getPathRestriction()
    subcontext._setObject('crit__path_ATRelativePathCriterion', b)
    c=getSortCriteria()
    subcontext._setObject("crit__created_ATSortCriterion", c)

def getFileRestriction():
    result=ATPortalTypeCriterion(id="crit__Type_ATPortalTypeCriterion",field="Type")
    result.value=(u"File",) 
    result.operator="and"
    return result
    
def getPathRestriction():
    result=ATRelativePathCriterion(id='crit__path_ATRelativePathCriterion', field="path")
    result.recurse=True
    result.relativePath='..'
    return result

def getSortCriteria():
    result=ATSortCriterion(id="crit__created_ATSortCriterion",field="created")
    result.revered=False
    return result

def post(context, event):
    catalog=event.newParent.portal_catalog
    event.newParent.updateforum(datetime.now())
    catalog.reindexObject(event.newParent)