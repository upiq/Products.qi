from Products.qi.util.lib.pyExcelerator import ImportXLS
import datetime
from qi.sqladmin import models as DB
import random
import os
import os.path
import time
      
def fromExcelDate(number):
    #correct python's library by 2 days
    basedate=datetime.date(1900,1,1)
    days=int(float(number))-2 # we don't actually want a time, if possible
    return basedate+datetime.timedelta(days)

def fromDashedDate(datestring):
    tup= time.strptime(datestring,"%Y-%m-%d")
    return datetime.date(tup[0],tup[1],tup[2])

def makeExcel(path):
    #because of the nature of the library,
    #a temporary file has to be created for it to read from
    #and additionally because we now retain data

    excel=ImportXLS.parse_xls(path)
    return excel

def getTeamFromNickName(nick,project):
    teams=project.team_set.all()

    identifiers=DB.TeamIdentifier.objects.filter(value=nick)
    if len(identifiers)==0:
        return None

    try:
        identifier=identifiers.get(team__in=teams)
        return identifier.team
    except AssertionError:
        return None
    except DB.TeamIdentifier.DoesNotExist:
        return None
    
def makeFile(originalfilename, fileobject,extension, group):
    randomNumbers=''
    trimmedname=originalfilename.split('\\')[-1]
    datedname="%s_%s"%(str(datetime.datetime.now()),trimmedname)
    
    filename='%s.%s'%(datedname,extension)
    folder='var/qiteamspace/uploads/%s'%group
    if not os.path.isdir(folder):
        os.makedirs(folder)
    path='%s/%s'%(folder,filename)
    tempfile=open(path,'w')
    tempfile.write(fileobject.read())
    tempfile.close()
    return filename, folder
