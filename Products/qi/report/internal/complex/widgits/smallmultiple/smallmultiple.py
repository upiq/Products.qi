


from zope.interface import implements
from zope.component.factory import Factory

#this pulls in all the various charting implements
from interfaces import ISmallMultiple

from qi.sqladmin import models as DB

from Products.qi.report.internal.complex.widgits.chart import Chart


        

class SmallMultiple(Chart):
    widgitname='small multiple'
    multiteam=False
    multimeasure=False
    implements(ISmallMultiple)
    def getMeasure(self):
        return self.getMeasures()[0]
    def getTeam(self):
        return self.getTeams()[0]
    def getValue(self, date):
        return self.valuefor(self.getMeasure(), self.getTeam(),date)
    def getTextBlurb(self):
        return self.getTeam().name
    def width(self):
        return 96
    def height(self):
        return 24
    

"""
from Products.Five.browser import BrowserView
class SmallMultipleApplyChanges(BrowserView):
    def __call__(self):
        self.context.measureid=int(self.context.request.form['measure'])
        self.context.teamid=int(self.context.request.form['team'])
        redirectTarget="%s/design"%self.context.charturl()
        self.context.request.response.redirect(redirectTarget)
"""


multiplefactory=Factory(SmallMultiple,title="Small Multiple Chart")