from Products.qi.extranet.types.interfaces import ITeam
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import decode
from Products.CMFDefault.utils import makeEmail
from Products.CMFDefault.utils import Message as _


def buildMail(message, address, subject, context,fromaddr, \
    grouping='All members',owner=None):
    #atool = getToolByName(context, 'portal_actions')
    #utool = getToolByName(context, 'portal_url')
    #portal_url = utool()

    
    options = {}
    options['password'] = 'hello'
    
    
    groupType='project'
    name='%s'%owner.getDBProject().name
    if hasattr(context, 'getDBTeam'):
        name='%s:%s'%(owner.getDBProject().name,owner.getDBTeam().name)
        groupType='team'
    
    headers = {}
    format='[QI %s %s update](%s) %s'
    headers['Subject'] = format%(groupType,name,grouping,subject)
    headers['From'] = '%s <%s>' % ('QI Project Mail Service',
                                   'testdev@qiteamspace-demo.com')
    headers['To'] = '<%s>' % (address)
    
    bodyformat="""Message from %s
    %s"""
    body=bodyformat%(fromaddr,message)
    
    extraheaders="""Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit"""
    emailformat='%s\nTo: %s\nFrom: %s\nSubject: %s\n\n%s'
    email=emailformat%(extraheaders,headers['To'],headers['From'],
        headers['Subject'],body)
    
    
    
    #mtext = context.listservEmail(
    #        user=fromaddr,
    #        text=message)
    #result = makeEmail(body, context, headers)
    return str(email)
    
    
    
    
def newBuildMail(message, address, subject, listservdomain, context,fromaddr, \
    grouping='All members',owner=None):
    #atool = getToolByName(context, 'portal_actions')
    #utool = getToolByName(context, 'portal_url')
    #portal_url = utool()

    
    options = {}
    options['password'] = 'hello'
    
    
    groupType='project'
    name='%s'%owner.getDBProject().name
    if isinstance(context, ITeam):
        name='%s:%s'%(owner.getDBProject().name,owner.getDBTeam().name)
        groupType='team'
    
    
    listservaddr='%s@%s'%(name,listservdomain)
    headers = {}
    format='[QI %s %s update](%s) %s'
    headers['Subject'] = format%(groupType,name,grouping,subject)
    headers['From'] = '%s <%s>' % ('QI-teamspace Mail Service',
                                   listservaddr)
    headers['To'] = '<%s>' % (address)
    
    bodyformat="""Message from %s
    %s"""
    body=bodyformat%(fromaddr,message)
    
    extraheaders=buildheaders('no information')
    

    emailformat='%s\nTo: %s\nFrom: %s\nSubject: %s\n\n%s'
    email=emailformat%(extraheaders,headers['To'],headers['From'],
        headers['Subject'],body)
    
    
    
    #mtext = context.listservEmail(
    #        user=fromaddr,
    #        text=message)
    #result = makeEmail(body, context, headers)
    return str(email)


def buildheaders(contentinfo):
    return """Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit"""
