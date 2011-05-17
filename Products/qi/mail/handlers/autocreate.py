from Products.CMFCore.utils import getToolByName
from psycopg2 import IntegrityError 

from django.contrib.auth.models import User 
from qi.sqladmin import models 
from datetime import datetime
from Products.qi.extranet.types.interfaces import ITeam
from zope.app.container.contained import ObjectAddedEvent
from Products.qi.util.logger import logger

from qi.sqladmin import models as DB

def addDefaultMailingList(projectorteam, addevent):
    if hasattr(projectorteam, 'getDBTeam'):
        project=addevent.newParent.getDBProject()
        #this line may not work, the code is a bit complicated to follow
        team=projectorteam.getDBTeam()
        pname=projectorteam.getTeam().id
        name=pname
        count=0
        while len(DB.MailingList.objects.filter(listname=name))>0:
            if count==0:
                tag=''
            else:
                tag='-%i'%count
            count+=1
            name='%s-%s%s'%(projectorteam.getProject().id,name,tag)
    else:
        project=projectorteam.getDBProject()
        pname=projectorteam.getProject().id
        name=pname
        count=0
        while len(DB.MailingList.objects.filter(listname=name))>0:
            if count==0:
                tag=''
            else:
                tag='-%i'%count
            count+=1
            name='members-%s%s'%(pname,tag)
        team=None
    print 'mailing lists already existing: %s'%\
        DB.MailingList.objects.filter(listname=name)
    members=DB.SpecialMailGroup.objects.get(groupname='members')
    deflist=DB.MailingList()
    deflist.project=project
    deflist.team=team
    deflist.description="Mailing list for %s members"%projectorteam.title
    deflist.listname=name
    deflist.joinable=False
    deflist.replyable=True
    try:
        deflist.save()
    except Exception, e:
        logger.handleException(e)
    deflist.groups.add(members)
