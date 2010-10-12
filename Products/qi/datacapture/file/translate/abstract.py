
class FileTranslator:
    
    #initially load data
    def loadData(self, filename):
        raise NotImplemented()
    
    #return the extension that the file on disk should have
    #DEPRECATED(hopefully not called)
    def extensionType(self):
        raise NotImplemented()
    
    #once the data is extracted from the file object in a format convenient for
    #our routine, then convert it to our rows (as a list)
    def getRows(self):
        raise NotImplemented()
    def getErrors(self):
        return {}