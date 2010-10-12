from interfaces import IParagraphWidgit, ILineWidgit, ITitleWidgit
from Products.qi.report.internal.complex.widgits.datatable import Widgit
from zope.component.factory import Factory
from zope.interface import implements

class Paragraph(Widgit):
    implements(IParagraphWidgit)
    text=""
    def displayblurb(self):
        """shows a paragraph"""
        return "<p>%s</p>"%self.text
    def editblurb(self):
        """gives a textarea to edit the paragraph"""
        return """
        <textarea name="%s/%s/displaytext">%s</textarea>
        """%(self.getrow().id, self.id, self.text)
    def updateOtherAttribute(self, attribute, value):
        if attribute=="displaytext":
            self.text=value
        else:
            raise NotImplementedError("only the text of paragraphs may be changed")

class Title(Widgit):
    implements(ITitleWidgit)
    text=""
    def displayblurb(self):
        """displays the header"""
        return "<h3>%s</h3>"%self.text
    def editblurb(self):
        """gives a simple edit field for the header"""
        return """
        <input type="text" name="%s/%s/displaytext" value="%s" />
        """%(self.getrow().id, self.id, self.text)
    def updateOtherAttribute(self, attribute, value):
        if attribute=="displaytext":
            self.text=value
        else:
            raise NotImplementedError("only the text of titles may be changed")

class Line(Widgit):
    implements(ILineWidgit)
    def displayblurb(self):
        """displays a simple line"""
        return "<hr />"
    def editblurb(self):
        """displays the line since we have nothing to edit about it"""
        return "<hr />"
        
        
        
paragraphfactory=Factory(Paragraph,title="paragraph")
titlefactory=Factory(Title,title="title")
linefactory=Factory(Line,title="line")