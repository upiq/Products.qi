from Products.Five.browser import BrowserView
class QueryData(BrowserView):
    def __call__(self, *args, **kw):
        self.measureA=self.context.measures()[0]
        self.measureB=self.context.measures()[1]
        form=self.request.form
        tqxinfo=form['tqx'].split(';')
        tqxdict={}
        for x in tqxinfo:
            key, value=x.split(':')
            tqxdict[key]=value
        if tqxdict.get('out','json')=='json':
            result=self.buildjsonresponse(**tqxdict)
        return result
    def buildjsonresponse(self, version='0.6',reqId=None,
                                out='json',responseHandler='google.visualization.Query.setResponse', 
                                **kw):
        format='%s({%s})'
        rows=self.buildrows()

        table="""cols:[
        {type:'string'},
        {type:'datetime'},
        {label:'%(measureA)s', type:'number'},
        {label:'%(measureB)s', type:'number'}
],
rows:[\n%(rows)s\n]"""%{'measureA':self.measureA.name,'measureB':self.measureB.name,'rows':rows}
        globalvars="""version: 0.6,
reqId:%(reqId)s,
status:'ok',
table:{%(table)s}"""%{'table':table, 'reqId':reqId}
        return format%(responseHandler,globalvars)
    
    def buildrows(self):
        result=""
        for team in self.context.teams():
            for date in self.context.dates():
                result+=self.buildrow(team, date)
        return result
    
    def buildrow(self, team, date):
        rowformat="         {c:[{v:'%(teamname)s'},{v:new Date(%(dateparams)s)},%(cellA)s,%(cellB)s]},\n"
        #rowformat="         {c:[{v:'%(teamname)s'},{v:'%(dateparams)s'},%(cellA)s,%(cellB)s]},\n"
        return rowformat%{'teamname':team.name.replace('\'','\\\''),
                            'dateparams':date.strftime('%Y, %m, %d, 0, 0, 0'),
                            #'dateparams':date.strftime('%m-%Y'),
                            'cellA':self.buildValueCell(self.measureA,team, date),
                            'cellB':self.buildValueCell(self.measureB,team, date)
                            }
    def buildValueCell(self,measure,team, date):
        value=self.context.valuefor(measure,team, date)
        if value:
            return '{v:%f}'%value
        return '{}'