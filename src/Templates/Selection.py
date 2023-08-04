from AnalysisG.Templates import ParticleTemplate
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Tools import Code, Tools
from time import time
import traceback
import statistics
try: import pyc
except: pass


class Neutrino(ParticleTemplate):
    def __init__(self):
        self.Type = "nu"
        ParticleTemplate.__init__(self)


class SelectionTemplate(Tools):
    def __init__(self):
        self.hash = None
        self.ROOTName = None
        self.Tree = None
        self.index = 0
        self.AllowFailure = False
        self.Residual = []
        self.CutFlow = {}
        self.Errors = {}
        self.TimeStats = []
        self.AllWeights = []
        self.SelWeights = []

    @property
    def _t1(self):
        self.__t1 = time()

    @property
    def _t2(self):
        self.TimeStats.append(time() - self.__t1)

    @property
    def AverageTime(self):
        return statistics.mean(self.TimeStats)

    @property
    def StdevTime(self):
        return statistics.stdev(self.TimeStats)

    @property
    def Luminosity(self):
        return ((sum(self.SelWeights))) / sum(self.AllWeights)

    @property
    def NEvents(self):
        return len(self.SelWeights)

    def Selection(self, event):
        return True

    def Strategy(self, event):
        pass

    def Px(self, val, phi):
        return pyc.Transform.Px(val, phi)

    def Py(self, val, phi):
        return pyc.Transform.Py(val, phi)

    def MakeNu(self, s_):
        if s_ == 0.0: return None
        if len(s_) == 0: return None
        nu = Neutrino()
        nu.px = s_[0]
        nu.py = s_[1]
        nu.pz = s_[2]
        #nu.e = (nu.px**2 + nu.py**2 + nu.pz**2) ** 0.5
        return nu

    def NuNu(
        self, q1, q2, l1, l2, ev,
        mT=172.5 * 1000, mW=80.379 * 1000, mN=0, zero=1e-12,
        gev = False
    ):
        scale = 1/1000 if gev else 1
        inpt = []
        inpt.append([[q1.pt*scale, q1.eta, q1.phi, q1.e*scale]])
        inpt.append([[q2.pt*scale, q2.eta, q2.phi, q2.e*scale]])
        inpt.append([[l1.pt*scale, l1.eta, l1.phi, l1.e*scale]])
        inpt.append([[l2.pt*scale, l2.eta, l2.phi, l2.e*scale]])

        inpt.append([[ev.met*scale, ev.met_phi]])
        inpt.append([[mW*scale, mT*scale, mN*scale]])
        inpt.append(zero)

        sol = pyc.NuSol.Polar.NuNu(*inpt)
        _s1, _s2, diag, n_, h_per1, h_per2, nsols = sol

        o = [[self.MakeNu(k), self.MakeNu(j)] for k, j in zip(_s1.tolist(), _s2.tolist())]
        return [p for p in o if p[0] != None and p[1] != None]

    def Nu(
        self, q1, l1, ev,
        S=[100, 0, 0, 100],
        mT=172.5*1000, mW=80.379*1000, mN=0, zero=1e-12,
        gev = False
    ):
        scale = 1/1000 if gev else 1

        inpt = []
        inpt.append([[q1.pt*scale, q1.eta, q1.phi, q1.e*scale]])
        inpt.append([[l1.pt*scale, l1.eta, l1.phi, l1.e*scale]])

        inpt.append([[ev.met*scale, ev.met_phi]])
        inpt.append([[mW*scale, mT*scale, mN*scale]])

        inpt.append([[S[0], S[1]], [S[2], S[3]]])
        inpt.append(zero)
        sol, chi2 = pyc.NuSol.Polar.Nu(*inpt)
        nus = [self.MakeNu(s) for s in sol.tolist()]
        return nus

    def Sort(self, inpt, descending=False):
        if isinstance(inpt, list):
            inpt.sort()
            return inpt
        _tmp = list(inpt)
        _tmp.sort()
        if descending: _tmp.reverse()
        inpt = {k: inpt[k] for k in _tmp}
        return inpt

    def _EventPreprocessing(self, event):
        self.AllWeights += [event.weight]

        if "Rejected-Selection" not in self.CutFlow:
            self.CutFlow["Rejected-Selection"] = 0
        if "Passed-Selection" not in self.CutFlow:
            self.CutFlow["Passed-Selection"] = 0

        if self.AllowFailure:
            try: res = self.Selection(event)
            except: res = False
        else: res = self.Selection(event)

        if res == False:
            self.CutFlow["Rejected-Selection"] += 1
            return False
        self.CutFlow["Passed-Selection"] += 1

        self._t1
        if self.AllowFailure:
            try: o = self.Strategy(event)
            except:
                self._t2
                string = ""
                if string not in self.Errors: self.Errors[string] = 0
                self.Errors[string] += 1
                return False
        else: o = self.Strategy(event)
        self._t2

        if isinstance(o, str) and "->" in o:
            if o not in self.CutFlow: self.CutFlow[o] = 0
            self.CutFlow[o] += 1
        else:
            self.Residual += [o] if o != None else []
        self.SelWeights += [event.weight]
        return True

    def __call__(self, Ana=None):
        if type(Ana).__name__ == "Event":
            return self._EventPreprocessing(Ana)
        if issubclass(type(Ana), SampleTracer) == False:
            return
        for i in Ana:
            self.hash = i.hash
            self.ROOTName = i.ROOT
            self._EventPreprocessing(i)

    def __eq__(self, other):
        if other == 0:
            return False
        x = Code(other)._Hash == Code(self)._Hash
        x *= other.Tree == self.Tree
        return x

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __add__(self, other):
        if other == 0:
            return self
        if other != self:
            return self

        keys = set(list(self.__dict__) + list(other.__dict__))
        for i in keys:
            if i.startswith("_SelectionTemplate"):
                continue
            if isinstance(self.__dict__[i], str):
                continue
            if isinstance(self.__dict__[i], bool):
                continue
            if i == "_CutFlow":
                k_ = set(list(self.__dict__[i]) + list(other.__dict__[i]))
                self.__dict__[i] |= {l: 0 for l in k_ if l not in self.__dict__[i]}
                other.__dict__[i] |= {l: 0 for l in k_ if l not in other.__dict__[i]}
            if i not in self.__dict__:
                self.__dict__[i] = other.__dict__[i]
                continue
            self.__dict__[i] = self.MergeData(self.__dict__[i], other.__dict__[i])

        out = self.__class__()
        out.hash = self.hash
        for i in self.__dict__:
            setattr(out, i, self.__dict__[i])
        return out

    @property
    def _dump(self):
        out = SelectionTemplate()
        for i in self.__dict__:
            out.__dict__[i] = self.__dict__[i]
        return out
