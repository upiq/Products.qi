from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from datetime import datetime
from django.core.paginator import Paginator
from Products.PythonScripts.standard import html_quote
from StringIO import StringIO
from Products.qi.datacapture.file.status.browser.uploads import DetailView
from time import strptime
import re

class XMLExport(DetailView):

    def __call__(self):
        query=self.getBaseQuery()
        query=self.applyFilters(query).order_by('series','team','measure','itemdate')
        from Products.qi.datacapture.file.export.exportthread import XMLExportThread
        batchjob=XMLExportThread(query, '/'.join(self.context.getPhysicalPath()))
        batchjob.start()
        self.context.request.response.redirect(self.context.absolute_url()+'/viewdata')
        
        return

class GetExportResult(BrowserPlusView):
    def __call__(self):
        response = self.context.request.response
        response.setHeader("Content-type","text/xml")
        response.setHeader("Content-disposition","attachment;filename=export.xml")
        return self.context.lastexport

class OldXMLExport(DetailView):
    def __call__(self):
        query=self.getBaseQuery()
        query=self.applyFilters(query).order_by('series','team','measure','itemdate')

        
        query=self.getBaseQuery()
        query=self.applyFilters(query).order_by('series','team','measure','itemdate')
        
        result= "<dataset>\n"+self.buildseries(query)+"\n</dataset>"

        
        response = self.context.request.response
        response.setHeader("Content-type","text/xml")
        response.setHeader("Content-disposition","attachment;filename=export.xml")
        #request.response.setHeader("Pragma","no-cache")
        return result
    
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
