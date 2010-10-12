
class UploadType:
    name=''
    command=''
    
    def getName(self):
        return self.name
    def getCommand(self):
        return self.command
    def setName(self,value):
        self.name=value
    def setCommand(self, value):
        self.command=value
    """this has a translator for one kind of upload"""