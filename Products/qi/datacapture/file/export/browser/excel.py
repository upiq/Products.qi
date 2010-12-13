from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from datetime import datetime
from django.core.paginator import Paginator
from Products.PythonScripts.standard import html_quote
from StringIO import StringIO
from Products.qi.datacapture.file.status.browser.uploads import DetailView
from xlwt import *


class ExcelExport(DetailView):
    colstart=2
    rowstart=0
    def __call__(self,*args,**kw):
        response=self.request.response
        response.setHeader("Content-type","application/vnd.ms-excel")
        response.setHeader("Content-disposition","attachment;filename=results.xls")
        return self.buildExcel(self.applyFilters(self.getBaseQuery()))
    
    def buildExcel(self,query):
        resultdata=StringIO()
        resultbook=Workbook()
        sheet=resultbook.add_sheet('exported_data')
        self.buildsheet(query,sheet)
        resultbook.save(resultdata)
        return resultdata.getvalue()
    
    def buildsheet(self,query, sheet):
        rows=self.findrows(query)
        columns=self.findcolumns(query)
        rownum=self.rowstart
        
        #write the base headers
        sheet.write(0,0,'Team Name')
        sheet.write(0,1,'Series')
        sheet.write(0,2,'Report Date')
        
        #write the column headers
        curcolumn=self.colstart
        for x in columns:
            curcolumn+=1
            measureobj=DB.Measure.objects.get(id=x)
            sheet.write(0,curcolumn, measureobj.shortname)
        
        for x in rows:
            subquery=self.filterForRow(query,x[0],x[1],x[2])
            if subquery.count()>0:
                if x[2] is not None:
                    seriesname=DB.Series.objects.get(id=x[2]).name
                else:
                    seriesname='Total Population'
                team=DB.Team.objects.get(id=x[0])


                rownum=rownum+1
                #write the header
                sheet.write(rownum,0,team.name)
                sheet.write(rownum,1,seriesname)
                sheet.write(rownum,2,x[1],easyxf(num_format_str='mm/dd/yyyy'))
                colnum=self.colstart
                for y in columns:
                    colnum=colnum+1
                    try:
                        result=subquery.get(measure=y)
                        sheet.write(rownum, colnum,result.value)
                    except DB.MeasurementValue.DoesNotExist:
                        sheet.write(rownum, colnum,None)
            else:
                #empty row probably just pass putting this here in case I think of something
                pass
    def findrows(self, query):
        result= query.values('team','itemdate','series').distinct()
        return [(x['team'],x['itemdate'],x['series']) for x in result]
    def findcolumns(self,query):
        result=query.values('measure').distinct()
        return [x['measure'] for x in result]
    
    def filterForRow(self, query, team, itemdate, series):
        if series is None:
            return query.filter(team__id=team, itemdate=itemdate, series__isnull=True)
        else:
            return query.filter(team__id=team, itemdate=itemdate, series__id=series)
        
            
    
    def findseries(self, query):
        result={}
        for x in query:
            if x.series is None:
                result[None]=None
            else:
                result[x.series]=None
        return result
