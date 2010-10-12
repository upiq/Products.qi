from datatable import Widgit
class Chart(Widgit):
    cachedimage=None
    def locationJS(self):
        
        return '''idval="%s/%s";
        basepath="%s/";
        chartwidth=%i;
        chartheight=%i;'''%(self.getrow().id,    self.id,
            self.absolute_url(), 
            self.width(), 
            self.height())
    def getTextBlurb(self):
        return ""
    def chartstyle(self):
        return """width: %spx;height: %spx; border-width: 0;"""%(self.width(),self.height())
    def width(self):
        return 400
    def height(self):
        return 400


from Products.Five.browser import BrowserView
from PIL import Image
from StringIO import StringIO

class ChartCacher(BrowserView):
    def __call__(self, *args, **kw):
        
        print "cache being readied"
        form=self.context.request.form
        width=int(form['width'])
        height=int(form['height'])
        result=Image.new('RGB', (width, height))
        for y in xrange(height):
            x=0
            row=form['r%i'%y].split(',')
            for cell in row:
                try:
                    color, count=cell.split(':')
                except ValueError:
                    color=cell
                    count=1
                count=int(count)
                color=int(color, 16)
                color=self.reversecolor(color)
                #print 'y: %s, count: %s, color: %x'%(y, count, color)
                for pixel in range(count):
                    result.putpixel((x,y),color)
                    x+=1
        savefile=StringIO()
        result.save(savefile, 'png')
        self.context.cachedimage=savefile.getvalue()
        self.context._p_changed=1
        savefile.close()
        self.context.request.RESPONSE.setHeader('Content-Type', 'image/png')
        return self.context.cachedimage
    def reversecolor(self,number):
        b=number//(256*256)
        g=(number//256)%256
        r=number%256
        return r*256*256+g*256+b

class ChartCacheValue(BrowserView):
    def __call__(self, *args, **kw):
        self.context.request.RESPONSE.setHeader('Content-Type', 'image/png')
        return self.context.cachedimage