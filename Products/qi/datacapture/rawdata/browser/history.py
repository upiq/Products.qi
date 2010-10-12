from Products.qi.util.general import BrowserPlusView
from qi.sqladmin import models as DB

class HistoryView(BrowserPlusView):
    def value(self):
        form=self.context.request.form
        if 'valueid' not in form:
            return None
        try:
            valueid=int(form['valueid'])
            value=DB.MeasurementValue.objects.get(id=valueid)
            return value
        except Exception:
            return None
    def link(self, tfile):
        if tfile is not None:
            format="%s/%s?fileid=%i"
            return format%(self.context.absolute_url(),"status",tfile.id)
        return 'javascript:void(0)'
    
    def history(self):
        value=self.value()
        changes=DB.MeasurementChange.objects.filter(value=value).order_by('-reportdate')
        previous=None
        result=[]
        for x in changes:
            if not previous or previous.oldvalue!=x.oldvalue or previous.oldannotation!=x.oldannotation:
                result.append(x)
            previous=x
        return result