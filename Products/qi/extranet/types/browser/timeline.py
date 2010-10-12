from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB
from Products.qi.util.logger import logger
from datetime import date

class TimelineView(BrowserPlusView):

    processFormButtons= ('submitdates',)
    
    def action(self, form, action):
        

        s=form["startdate"].strip().split("/")
        e=form["enddate"].strip().split("/")
        
        #separates the input into YYYY/MM/DD format for postgresql
        sdate= date(int(s[2]), int(s[0]), int(s[1]))
        edate= date(int(e[2]),int(e[0]), int(e[1]))
        
        
        project= self.context.getDBProject()
         
        project.startdate= sdate
        project.enddate = edate
        
        
        try:
            project.save()
        except Exception, e:
            logger.handleException(e)
            
        
    def validate(self, form):
        self.requiredDate('startdate','Start Date')
        self.requiredDate('enddate', 'End Date')
        

        
    def projectTimelineExists(self):
        #for pt file to call to see if dates exist
        project = self.context.getDBProject()
        if project.startdate is None and project.enddate is None:
            return False
        else:
            return True
            
    def showStartDate(self):
        #pt file calls to display existing dates
        project = self.context.getDBProject()
        return project.startdate.strftime("%m/%d/%Y")
    
    def showEndDate(self):
        
        project = self.context.getDBProject()
        return project.enddate.strftime("%m/%d/%Y")
        

        

       


