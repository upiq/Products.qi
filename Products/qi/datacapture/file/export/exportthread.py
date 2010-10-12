from threading import Thread, currentThread
from datetime import datetime
import os
import re
import time
import sys
import ZODB, transaction
import ZEO.ClientStorage
from ZODB import FileStorage, DB as ZopeDB


class XMLExportThread(Thread):
    def __init__(self,query, path):
        Thread.__init__(self)
        self.query=query
        self.path=path
        #import Zope2
        #app=Zope2.app()
        #print 'app gotted'
    def getContext(self):
        from Products.qi.mail.newListener import clientport
        self.storage=ZEO.ClientStorage.ClientStorage(('localhost', clientport))
        self.db=ZopeDB(self.storage)
        self.connection=self.db.open()
        self.root=self.connection.root()
        app=self.root['Application']
        return app.unrestrictedTraverse(self.path)
    def run(self):
        self.context=self.getContext()

        import transaction
        self.context.exportingXML=True
        self.context._p_changd=1
        transaction.commit()
        result= "<dataset>\n"+self.buildseries(self.query)+"\n</dataset>"
        transaction.abort()
        self.context.exportingXML=False
        self.context.lastexport=result
        self.context.lastexporttime=datetime.now()
        self.context._p_changed=1
        transaction.commit()
    def buildseries(self, query, indentation='  '):
        serieses=sorted(list(set([x.series for x in query])))
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
                    override=datetime(*strptime(found.group(1),"%m-%d-%Y")[:3])
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

        return """%(indentation)s<value>%(value)s</value>
%(indentation)s<annotation>%(annotation)s</annotation>"""%{'indentation':indentation,
            'value':self.escape(value), 'annotation':self.escape(annotation)}

    def escape(self, value):
        if value is None:
            return ''
        return value.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')