from Products.qi.report.internal.complex.widgits.interfaces import IChartWidgit

class IBigChart(IChartWidgit):
    def chartTitle(self):
        """different kinds of big charts will have different titles
        such as team name, or measure name."""
    #other requirements soon

class IControlChart(IBigChart):
    pass