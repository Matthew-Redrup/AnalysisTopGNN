from AnalysisG.Plotting import TLine, CombineTLine 
from AnalysisG.Plotting import TH1F, CombineTH1F
from sklearn.metrics import roc_curve, auc
from AnalysisG.IO import PickleObject
from time import time 
import numpy as np
import torch

class Metrics:
    def __init__(self):
        self.roc = {"truth" : [], "pscore": [], "dim" : 0}
        self.losshist = []
        self.accuracyhist = []
        self.mass = []
        self.mass_t = []
        self.nreco = []
        self.ntru = []
        self.nodes = []
        self.mode = None 
        self.out = {}

    @property
    def ROC(self):
        truth = torch.tensor(self.roc["truth"])
        pscores = torch.tensor(self.roc["pscore"])
        out = []
        for i in range(self.roc["dim"]-1):
            fpr, tpr, _ = roc_curve(np.array(truth.view(-1)), np.array(pscores[:, i+1].view(-1)))
            fpr, tpr = fpr.tolist(), tpr.tolist()
            a = float(auc(fpr, tpr))
            t = TLine()
            t.Title = self.mode
            t.xData = fpr
            t.xTitle = "False Positive Rate"
            t.yData = tpr
            t.yTitle = "True Positive Rate"
            self.out[i] = {"auc" : a}
            out.append(t)
        return out

    @property 
    def LossHist(self):
        th = TH1F()
        th.xData = self.losshist 
        th.xBins = 100
        th.Title = self.mode
        th.LaTeX = False
        th.xTitle = "Loss"
        return th

    @property
    def AccuracyHist(self):
        th = TH1F()
        th.xBins = 100
        th.xData = self.accuracyhist 
        th.Title = self.mode
        th.LaTeX = False
        th.xTitle = "Accuracy"
        return th

    @property
    def MassHist(self):
        if len(self.mass) == 0: return  
        th = TH1F()
        th.xBins = 500
        th.xMin = 0
        th.xData = self.mass 
        th.Title = self.mode
        th.LaTeX = False
        th.xTitle = "Mass (GeV)"
        return th

    @property 
    def MassTHist(self):
        if len(self.mass_t) == 0: return        
        th = TH1F()
        th.xBins = 500
        th.xMin = 0
        th.xData = self.mass_t
        th.LaTeX = False
        th.Title = "truth"
        th.xTitle = "Mass (GeV)"
        return th
       
    @property 
    def recoHist(self):
        if len(self.nreco) == 0: return        
        th = TH1F()
        th.xData = self.nreco
        th.Title = self.mode
        th.LaTeX = False
        th.xTitle = "Number of Particles Reconstructed"
        return th

    @property 
    def ntruHist(self):
        if len(self.ntru) == 0: return 
        th = TH1F()
        th.xData = self.ntru
        th.xMin = 0
        th.Title = "truth"
        th.LaTeX = False
        th.xTitle = "True Number of Particles"
        return th
 
    @property 
    def NodeHist(self):
        th = TH1F()
        th.xData = self.nodes
        th.Title = self.mode
        th.xBins = max(self.nodes)+1
        th.xMin = 0
        th.xMax = max(self.nodes)
        th.LaTeX = False
        th.xTitle = "n-Nodes"
        return th
 
class Epoch:

    def __init__(self):
        self.Epoch = None
        self.RunName = None
        self.OutputDirectory = None
        self.train = None
        self._train = {}
        self._val = {}
        self._timer = []

        self.o_model = {}
        self.i_model = {}

    @property 
    def start(self):
        self._t1 = time()

    @property 
    def end(self):
        self._timer.append(time() - self._t1)

    @property
    def init(self):
        self._train = {i[2:] : {
                    "pred" : [], "truth"  : [], 
                    "acc"  : [], "loss"   : [], 
                    "mass" : [], "mass_t" : [], 
                    "nrec" : [], "ntru"   : []
                } for i in self.o_model
        }
        self._val = {i[2:] : {
                    "pred" : [], "truth"  : [], 
                    "acc"  : [], "loss"   : [], 
                    "mass" : [], "mass_t" : [], 
                    "nrec" : [], "ntru"   : []
                } for i in self.o_model
        }
        self._train["nodes"] = []
        self._val["nodes"] = []

    def Collect(self, truth, pred, loss):
        lst = self._train if self.train else self._val 
        nodes = truth.num_nodes.tolist()
        if isinstance(nodes, list): lst["nodes"] += nodes
        else: lst["nodes"] += [nodes]
        for o, t in zip(self.o_model, self.o_model.values()):
            feat = o[2:]
            lst[feat]["pred"] += getattr(pred, t).tolist()
            lst[feat]["truth"] += getattr(truth, t).tolist()
            lst[feat]["acc"] += [loss[feat]["acc"].tolist()]
            lst[feat]["loss"] += [loss[feat]["loss"].tolist()]

    def _makehists(self, dic, mode):
        out = {}
        for i in dic:
            if i == "nodes": continue
            m = Metrics()
            m.roc["truth"] = dic[i]["truth"]
            m.roc["pscore"] = dic[i]["pred"]
            m.roc["dim"] = len(dic[i]["pred"][0])
            m.losshist = dic[i]["loss"]
            m.accuracyhist = dic[i]["acc"]
            m.mass = dic[i]["mass"]
            m.mass_t = dic[i]["mass_t"] 
            m.nreco = dic[i]["nrec"]
            m.ntru = dic[i]["ntru"]
            m.mode = mode
            out[i] = m 
        m = Metrics()
        m.nodes = dic["nodes"]
        m.mode = mode
        out["nodes"] = m
        return out

    def plots(self, title, a, b, c = None, d = None):
        if a == b: return 
        th = CombineTH1F()
        th.Histograms += [a, b] 
        if c is not None: th.Histograms += [c]
        if d is not None: th.Histograms += [d]
        try: d, t = title.split("/")
        except: d, t = "", title
        th.Title = title.replace("/", "-")
        th.Filename = t
        th.LaTeX = False
        th.OutputDirectory = self.OutputDirectory + "/" + self.RunName + "/" + self.Epoch + "/" + d
        th.Verbose = 0
        th.xMin = 0
        th.SaveFigure()

    @property
    def dump(self):
           
        train = self._makehists(self._train, "train")
        val = self._makehists(self._val, "validation")
        self.plots("Nodes", train["nodes"].NodeHist, val["nodes"].NodeHist)
        for i in self.o_model: 
            t, v = train[i[2:]], val[i[2:]]
            self.plots(i[2:] + "/Loss", t.LossHist, v.LossHist)
            self.plots(i[2:] + "/Accuracy", t.AccuracyHist, v.AccuracyHist)
            try:
                x, y = v.ROC[0], t.ROC[0]
                tc = CombineTLine()
                tc.LaTeX = False
                tc.title = i[2:]
                tc.Lines = [x, y]
                tc.OutputDirectory = self.OutputDirectory + "/" + self.RunName + "/" + self.Epoch
                tc.Filename = i[2:] + "/ROC" 
                tc.Verbose = 0
                tc.SaveFigure()
            except IndexError: pass
            if v.MassTHist.xData == None: continue
            t.MassTHist.xData += v.MassTHist.xData
            self.plots(i[2:] + "/Mass", t.MassTHist, v.MassHist, t.MassHist)

        PickleObject(self, self.OutputDirectory + "/" + self.RunName + "/" + str(self.Epoch) + "/Stats")
