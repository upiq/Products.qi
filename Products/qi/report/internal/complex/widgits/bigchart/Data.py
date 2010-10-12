
class ChartData:
    def dates(self):
        return context.dates()
    def measures(self):
        return context.measures()
    def teams(self):
        return context.teams()
    
    def valuefor(self,*args):
        return context.valuefor(*args)
        