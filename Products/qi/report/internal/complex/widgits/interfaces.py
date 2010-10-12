from zope.interface import Interface

class IWidgit(Interface):
    def typename(self):
        """This just returns the type of the widgit"""
    
    def printtag(self):
        """Widgits will need to present a print version of themselves.
        this may be the same for some, but not all"""
    
    

class IDataTable(IWidgit):
    def getGrouping(self):
        """how to group elements within this table"""


class IChartWidgit(IWidgit):
    
    def cacheprintdata(self, data):
        """It is essential that all charts cache printable data they receive, which
        is (in theory) triggered by a print button on the chart page"""
        


