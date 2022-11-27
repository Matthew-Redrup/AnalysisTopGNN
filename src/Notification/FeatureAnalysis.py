from .Notification import Notification
import sys

class FeatureAnalysis(Notification):

    def __init__(self):
        pass

    def FeatureFailure(self, name, mode, EventIndex):
        try:
            EventIndex = " :: File " + "/".join(self.IndexToROOT(EventIndex).split("/")[-2:])
        except: 
            EventIndex = ""

        fail = str(sys.exc_info()[1]).replace("'", "").split(" ")
        self.Failure("(" + mode + "): " + name + " ERROR -> " + " ".join(fail) + EventIndex)

    def TotalFailure(self):
        string = "Feature failures detected... Exiting"
        self.Failure("="*len(string))
        self.FailureExit(string)

    def PassedTest(self, name, mode):
        self.Success("!!!(" + mode + ") Passed: " + name)
