from .Hashing import Hashing

class EventContainer(Hashing):

    def __init__(self):
        self.Trees = {}
        self.EventIndex = 0
        self.Filename = None

    def MakeEvent(self, ClearVal):
        for i in self.Trees:
            self.Trees[i]._Compile(ClearVal)
            self.Filename = self.MD5(self.Filename + "/" + str(self.Trees[i]._SampleIndex))
    
    def MakeGraph(self):
        for i in self.Trees:
            self.Trees[i] = self.Trees[i].ConvertToData()
        return self
