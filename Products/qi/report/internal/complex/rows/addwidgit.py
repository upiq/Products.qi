from Products.qi.util.general import BrowserPlusView
from Acquisition import aq_parent
from zope.component import getUtility
from Products.qi.report.internal.complex.interfaces import IChartHolder


from Products.qi.report.internal.complex.widgits.bigchart.bigchart import measurefactory, teamfactory, controlfactory
from Products.qi.report.internal.complex.widgits.simple.widgits import linefactory, titlefactory, paragraphfactory
from Products.qi.report.internal.complex.widgits.datatable import tablefactory, annotationfactory
from Products.qi.report.internal.complex.widgits.google.content import googlefactory
from Products.qi.report.internal.complex.widgits.smallmultiple.smallmultiple import multiplefactory

class AddWidgit(BrowserPlusView):
    processFormButtons=('add',)
    def validate(self, form):
        self.requiredInForm('type')
        
    addedtypes={ 'datatable':tablefactory,
    'smallmultiple':multiplefactory,
    'teamchart':teamfactory,
    'measurechart':measurefactory,
    'line':linefactory,
    'title': titlefactory,
    'paragraph': paragraphfactory,
    'annotations':annotationfactory,
    'googlemotion':googlefactory,
    'controlchart':controlfactory,
    }
    def action(self,form, action):
        addtype=form['type']
        added=self.addedtypes.get(addtype, None)
        if added is None:
            raise NotImplementedError(addtype+' is not a valid type')
        #build it
        added=added()
            
        #assign it
        self.context.addwidgitobject(added)
        target=self.context[added.id]
        redirectTarget="%s/editblurb"%target.absolute_url()
        self.context.request.response.redirect(redirectTarget)

class DeleteWidgit(BrowserPlusView):
    
    processFormButtons=('deletedid',)
    def validate(self, form):
        result=self.requiredInForm('deletedid')
        print 'result was ', result
    def action(self, form, action):
        deletedid=form['deletedid']
        delattr(self.context,deletedid)
        self.context._p_changd=1
        redirectTarget="%s/design"%self.context.charturl()
        self.context.request.response.redirect(redirectTarget)