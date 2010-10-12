from Products.qi.util.general import BrowserPlusView
from kss.core.ttwapi import startKSSCommands
from kss.core.ttwapi import getKSSCommandSet
from kss.core.ttwapi import renderKSSCommands
from qi.sqladmin import models as DB
from Products.qi.util import utils
import AccessControl



class KSSAction(BrowserPlusView):
    errorid='errors'

    def __call__(self, *args, **kw):
        startKSSCommands(self.context, self.context.REQUEST)
        core=getKSSCommandSet('core')
        if self.condition():
            self.doKss(core)
            self.customKss(core)
        if self.hasErrors():
            self.renderErrors(core)
        else:
            self.clearErrors(core)
        commands= renderKSSCommands()
        return commands
        
    def renderErrors(self, core):
        rowformat="<li>%s</li>"
        rows=""
        selector="#%s"%self.errorid
        htmlformat="""
<div class="error" id="%s">
<ul>
%s
</ul>
</div>
"""
        for values in self.errors.itervalues():
            for value in values:
                rows+=rowformat%value
        html=htmlformat%(self.errorid,rows)
        core.replaceHTML(selector, html)
        

    def clearErrors(self, core):
        html='<div id="%s"></div>'%self.errorid
        selector='#%s'%self.errorid
        core.replaceHTML(selector, html)
        
    def condition(self):
        self.errors={}
        self.validate()
        return not self.hasErrors()
    
    def validate(self):
        pass
        
    def doKss(self,core):
        pass
    
    def customKss(self, core):
        pass

class KSSHtmlRenderer(KSSAction):
    def getTarget(self):
        return 'nowhere'
    def buildHtml(self):
        return self.index()
    def doRender(self,core, html, target):
        pass
    def doKss(self, core):
        html=self.buildHtml()
        target='#%s'%self.getTarget()
        self.doRender(core, html,target)

class KSSInnerWrapper(KSSHtmlRenderer):
    def doRender(self,core,html, target):
        core.replaceInnerHTML(target,html)

class KSSReplaceWrapper(KSSHtmlRenderer):
    def doRender(self, core,html, target):
        core.replaceHTML(target,html)
        
        
class KSSAddWrapper(KSSHtmlRenderer):
    def doRender(self, core,html, target):
        core.insertHTMLAsLastChild(target,html)
        
                
class SimpleResponse(KSSInnerWrapper):
    #just a placeholder
    def buildHtml(self, *args,**kw):
        return '<h2>apples</h2>'