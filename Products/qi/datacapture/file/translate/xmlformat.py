from xml.dom.minidom import parse
from abstract import FileTranslator
from copy import copy as shallowcopy
from Products.qi.datacapture.file.uploads.Row import Row

class TeamInfo:
    measures=None
    nicknames=None
    def __init__(self):
        self.measures={}
        self.nicknames=[]

class XMLTranslator(FileTranslator):
    
    #initially load data
    rows=[]
    def loadData(self, filename):
        self.rows=[]
        xml=parse(filename).documentElement
        serieses={}
        #assert we've been a dataset
        assert xml.nodeName=='dataset'
        for series in xml.getElementsByTagName('series'):
            try:
                seriesname=series.attributes['name'].value
            except KeyError:
                seriesname=None
            serieses[seriesname]=self.processSeries(series)
        #now linearize the dictionary
        self.rows= self.linearize(serieses)
    
    def linearize(self, data):
        result=[]
        added=Row()
        added.datetype='dashed'
        rownum=0
        #one big loop seemed painful but more clear than some super-recursive nightmare
        for added.series in data.keys():
            teams=data[added.series]
            for _team in teams.keys():
                added.team=teams[_team].nicknames
                measures=teams[_team].measures
                for added.measure in measures.keys():
                    periods=measures[added.measure]
                    for added.period in periods.keys():
                        submissions=periods[added.period]
                        for added.date in submissions.keys():
                            realadded=shallowcopy(added)
                            rownum+=1
                            #confusing but this is a tuple of value, annotation as returned by processsubmission
                            realadded.value, realadded.annotation=submissions[added.date]
                            realadded.rownum=rownum
                            result.append(realadded)
        return result
        
                        
    
    def processSeries(self, seriesElement):
        teams={}
        for team in seriesElement.getElementsByTagName('team'):
            teams[team.attributes['name'].value]=self.processTeam(team)
        return teams
    
    def processTeam(self, teamElement):
        data=TeamInfo()
        #just a bit different because teams have nicknames in addition to regular data
        for measure in teamElement.getElementsByTagName('measure'):
            data.measures[measure.attributes['name'].value]=self.processMeasure(measure)
        for nickname in teamElement.getElementsByTagName('nickname'):
            text=[x.data for x in nickname.childNodes]
            data.nicknames.append(' '.join(text))
        data.nicknames.append(teamElement.attributes['name'].value)
        return data
    def processMeasure(self, measureElement):
        periods={}
        for period in measureElement.getElementsByTagName('reportperiod'):
            periods[period.attributes['name'].value]=self.processPeriod(period)
        return periods
    
    def processPeriod(self, periodElement):
        submissions={}
        for submission in periodElement.getElementsByTagName('submission'):
            submissions[submission.attributes['name'].value]=self.processSubmission(submission)
        return submissions
    
    def processSubmission(self, submissionsElement):
        value=None
        annotation=None
        for _value in submissionsElement.getElementsByTagName('value'):
            value=' '.join([x.data for x in _value.childNodes])
        for _note in submissionsElement.getElementsByTagName('annotation'):
            annotation=' '.join([x.data for x in _note.childNodes])
        return (value, annotation)
    
    def processrow(self, row):
        result=Row()
        result.datetype='dashed'
        fix={"reportdate":"date"}
        for x in row.childNodes:
            if x.nodeType==row.ELEMENT_NODE:
                if x.firstChild is not None:
                    data=x.firstChild.data.strip()
                else:
                    data=''
                setattr(result,fix.get(x.nodeName,x.nodeName),data)
        return result
        
    
    #return the extension that the file on disk should have
    #DEPRECATED(hopefully not called)
    def extensionType(self):
        return '.xml'
    
    #once the data is extracted from the file object in a format convenient for
    #our routine, then convert it to our rows (as a list)
    def getRows(self):
        return self.rows
    def getErrors(self):
        return {}