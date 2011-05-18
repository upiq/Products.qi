from plone.app.form import base
from Products.qi.util import utils
from zope.component import createObject
from Products.qi.report.internal.complex.interfaces import IChartHolder
from zope.formlib import form
from Products.qi.util.general import BrowserPlusView
fields=form.Fields(IChartHolder)
from Products.qi import MessageFactory as _


class AddForm(base.AddForm):
    form_fields=fields
    def setUpWidgets(self, ignore_request=False):
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=ignore_request)

    def create(self, data):
        chart = createObject(u"qi.ChartHolder")
        form.applyChanges(chart, self.form_fields, data)
        return chart
fields=form.Fields(IChartHolder)
class EditForm(base.EditForm):
    form_fields=fields
    label=_(u"Edit")
    form_name=_(u"Edit")

class ChartPresentation(BrowserPlusView):
    removeBorders=False
    pass


class AssignCharts(BrowserPlusView):
    removeBorders=False
    processFormButtons=("insert","moveup","movedown","updateall")
    def validate(self, form):
        pass
    def insert(self,form):
        rowid=int(form['insertbefore'])
        self.context.addRow(rowid)
    
    def move(self, form, direction):
        moved=self.context[form['rowid']]
        moved.rowindex+=direction
        for x in self.context.rows():
            if x.rowindex==moved.rowindex and x!=moved:
                x.rowindex-=direction
        self.context.orderObjects('rowindex',False)
        
    def action(self, form, action):
        if action=="insert":
            self.insert(form)
        if action=="moveup":
            self.move(form,1)
        if action=="movedown":
            self.move(form,-1)
        if action=="updateall":
            for x in form:
                parts=x.split('/')
                if len(parts)==3:
                    self.updateItem(parts, form[x])
    def updateItem(self, parts, value):
        if value=='':
            value=[]
        elif isinstance(value, list):
            value=value[1:]
            
        rowname, widgitname, attribute=parts
        row=getattr(self.context,rowname)
        widgit=getattr(row, widgitname)
        widgit.cache=None
        widgit.cachetime=None
        if attribute=='teams':
            widgit.setTeams(value)
        elif attribute=='measures':
            widgit.setMeasures(value)
        elif attribute=='printonly':
            if value[0]=='on':
                widgit.printonly=True
            else:
                widgit.printonly=False
        else:
            widgit.updateOtherAttribute(attribute, value)
        
            
