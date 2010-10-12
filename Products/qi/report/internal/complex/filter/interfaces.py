from zope.interface import Interface

class IDataFilter(Interface):
    def ReduceDataset(self, data):
        """The jist of this function is that any dataset will be filtered several times
        over a chart to limit to the appropriate dates, teams, measures, etc."""
    
    