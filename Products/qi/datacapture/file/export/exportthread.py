from threading import Thread, currentThread
from datetime import datetime
import os
import re
import time
import sys
import transaction

from Products.qi.util.zodbconn import new_approot


class XMLExportThread(Thread):
    def __init__(self,query, path):
        Thread.__init__(self)
        self.query=query
        self.path=path
        self.progress=0
        self.target=query.count()
        
    def run(self):
        conn, approot = new_approot() #use zconfig, get conn, app
        self.context = approot.unrestrictedTraverse(self.path)
        self.context.exportingXML=True
        self.context._p_changd=1
        self.context.exportprogress=0
        self.context.exporttarget=self.target
        txn = transaction.get()
        txn.note('/'.join(self.context.getPhysicalPath()))
        txn.note('Flagged context as starting export of XML')
        txn.commit()
        #result= "<dataset>\n"+self.buildseries(self.query)+"\n</dataset>"
        result=self.fastbuild(self.query)
        txn = transaction.get()
        txn.abort()
        self.context.exportingXML=False
        self.context.lastexport=result
        self.context.lastexporttime=datetime.now()
        self.context._p_changed=1
        txn = transaction.get()
        txn.note('/'.join(self.context.getPhysicalPath()))
        txn.note('Flagged context as complete in exporting XML')
        txn.commit()
        conn.close() #thread is done running, close connection
    
    def fastbuild(self, query):
        from xml.dom.minidom import getDOMImplementation

        impl = getDOMImplementation()
        query=query.select_related().order_by('series','team','measure','itemdate','reportdate','value','annotation')
        self.seriesXML=None
        series="Needs to be something besides none, this string is unlikely to crop up"
        self.teamXML=None
        team=None
        self.measureXML=None
        measure=None
        self.itemdateXML=None
        itemdate=None
        lastmeasure=None
        self.xmlDoc=impl.createDocument(None, "dataset", None)
        self.datasetXML=self.xmlDoc.documentElement
        for record in query:
            if record.series!=series:
                series=record.series
                team=None
                self.addSeriesNode(series, record)
            if record.team!=team:
                team=record.team
                measure=None
                self.addTeamNode(team, record)
            if record.measure!=measure:
                self.fixMeasure(lastmeasure)
                measure=record.measure
                #doubling up this tracking variable so we can clean up more easily
                lastmeasure=measure
                itemdate=None
                self.addMeasureNode(measure,record)
            if record.measure.userdefined and record.measure.userdefined.find('excludeXML')>-1:
                continue
            if record.itemdate!=itemdate:
                itemdate=record.itemdate
                self.addPeriodNode(itemdate,record)
            self.addValueNode(record)
        return self.xmlDoc.toprettyxml()

    def fixMeasure(self,measure):
        if self.measureXML is None:
            return
        maxdate=None
        if measure.userdefined and measure.userdefined.find('forceperiod')>-1:
            found=re.search('forceperiod\\((.*)\\)', measure.userdefined)
            if found:
                override=datetime(*time.strptime(found.group(1),"%m-%d-%Y")[:3])
                count=0
                for reportPeriod in self.measureXML.childNodes:
                    if count==0:
                        reportPeriod.setAttribute('name',override.strftime("%Y-%m-%d"))
                    else:
                        self.measureXML.removeChild(reportPeriod)
                    count+=1
            
    def addSeriesNode(self,series, record):
        self.seriesXML=self.xmlDoc.createElement('series')
        if record.series is None:
            self.seriesXML.setAttribute('name','Total Population')
        else:
            self.seriesXML.setAttribute('name',record.series.name)
        self.datasetXML.appendChild(self.seriesXML)
    
    def addTeamNode(self, team,record):
        self.teamXML=self.xmlDoc.createElement('team')
        self.teamXML.setAttribute('name',record.team.name)
        self.seriesXML.appendChild(self.teamXML)
        nicknames=team.teamidentifier_set.all()
        for nickname in nicknames:
            nicknameXML=self.xmlDoc.createElement('nickname')
            nicknameText=self.xmlDoc.createTextNode(nickname.value)
            nicknameXML.appendChild(nicknameText)
            self.teamXML.appendChild(nicknameXML)
    def addMeasureNode(self,measure, record):
        self.measureXML=self.xmlDoc.createElement('measure')
        self.measureXML.setAttribute('name',measure.shortname)
        self.teamXML.appendChild(self.measureXML)
    def addPeriodNode(self,period, record):
        self.itemdateXML=self.xmlDoc.createElement('reportperiod')

        self.itemdateXML.setAttribute('name',record.itemdate.strftime("%Y-%m-%d"))
        self.measureXML.appendChild(self.itemdateXML)
    def addValueNode(self, record):
        #print self.measureXML.toxml(), record.value, record.measure
        dateXML=self.xmlDoc.createElement('submission')
        dateXML.setAttribute('name',record.reportdate.strftime("%Y-%m-%d"))
        valueXML=self.xmlDoc.createElement('value')
        annotationXML=self.xmlDoc.createElement('annotation')
        valueXML.appendChild(self.xmlDoc.createTextNode(record.value))
        annotationXML.appendChild(self.xmlDoc.createTextNode(record.annotation or ''))
        dateXML.appendChild(valueXML)
        dateXML.appendChild(annotationXML)
        self.itemdateXML.appendChild(dateXML)
    
    def buildseries(self, query, indentation='  '):
        print 'starting series'
        #serieses=sorted(list(set([x.series for x in query])))
        result=""
        for series in serieses:
            if series is None:
                subset=query.filter(series__isnull=True)
                seriesname='Total Population'
            else:
                subset=query.filter(series=series)
                seriesname=self.escape(series.value)
            newindentation=indentation+'  '
            result+="""%(indentation)s<series name="%(name)s">
%(data)s%(indentation)s</series>
"""%{'indentation':indentation,
                'data':self.buildteams(subset, newindentation),
                'name':seriesname or "Total Population"}
        return result
    def buildteams(self, query, indentation='  '):
        print 'starting teams'
        teams=sorted(list(set([x.team for x in query])))
        result=""
        for team in teams:
            subset=query.filter(team=team)
            latest=max([x.itemdate for x in subset])
            newindentation=indentation+'  '
            result+="""%(indentation)s<team name="%(name)s">
%(nicknames)s
%(data)s%(indentation)s</team>
"""%{'indentation':indentation,
                'nicknames':self.buildnicknames(team, indentation),
                'data':self.buildmeasures(subset, newindentation, latest),
                'name':self.escape(team.name)  }
        return result

    def buildnicknames(self, team, indentation='  '):
        return "\n".join([indentation+"<nickname>%s</nickname>"%self.escape(x.value) for x in team.teamidentifier_set.all()])

    def buildmeasures(self, query, indentation='  ',latestdate=None):
        print 'starting measures'
        measures=sorted(list(set([x.measure for x in query])))
        result=""
        for measure in measures:
            if measure.userdefined and measure.userdefined.find('excludeXML')>-1:
                continue
            subset=query.filter(measure=measure)
            if measure.userdefined and measure.userdefined.find('forceperiod')>-1:
                lastdate=max([x.itemdate for x in subset])
                subset=subset.filter(itemdate=lastdate)
                found=re.search('forceperiod\\((.*)\\)', measure.userdefined)
                if found:
                    override=datetime(*time.strptime(found.group(1),"%m-%d-%Y")[:3])
                else:
                    override=latestdate
            else:
                override=None

            newindentation=indentation+'  '
            result+="""%(indentation)s<measure name="%(name)s">
%(data)s%(indentation)s</measure>
"""%{'indentation':indentation,
                'data':self.builddates(subset, newindentation, override),
                'name':self.escape(measure.shortname)  }
        return result

    def builddates(self, query, indentation='  ', periodoverride=None):
        dates=sorted(list(set([x.itemdate for x in query])))
        result=""
        for date in dates:
            subset=query.filter(itemdate=date)
            if periodoverride is not None:
                date=periodoverride
            newindentation=indentation+'  '
            result+="""%(indentation)s<reportperiod name="%(name)s">
%(data)s%(indentation)s</reportperiod>
"""%{'indentation':indentation,
                'data':self.buildsubmissions(subset, newindentation),
                'name':date.strftime("%Y-%m-%d")  }
        return result


    def buildsubmissions(self, query, indentation='  '):
        #TODO: expand this to include historical values
        reportdates=sorted(list(set([x.reportdate for x in query])))
        result=""
        for date in reportdates:
            subset=query.filter(reportdate=date)
            newindentation=indentation+'  '
            result+="""%(indentation)s<submission name="%(name)s">
%(data)s
%(indentation)s</submission>
"""%{'indentation':indentation,
                'data':self.buildvalue(subset, newindentation),
                'name':date.strftime("%Y-%m-%d")  }
        return result

    def buildvalue(self, query, indentation):
        value=query[0].value
        annotation=query[0].annotation
        self.progress+=1
        if self.progress%1000==0:
            self.context.exportprogress=self.progress
            self.context.exporttarget=self.target
            self.context._p_changed=1
            print 'progress update', self.progress, self.target
            txn = transaction.get()
            txn.note('/'.join(self.context.getPhysicalPath()))
            txn.note('Flagged context XML export progress')
            txn.commit()
        return """%(indentation)s<value>%(value)s</value>
%(indentation)s<annotation>%(annotation)s</annotation>"""%{'indentation':indentation,
            'value':self.escape(value), 'annotation':self.escape(annotation)}

    def escape(self, value):
        if value is None:
            return ''
        return value.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
