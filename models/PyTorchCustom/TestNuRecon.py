from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event
import PyC.NuSol.Tensors as NuT
import PyC.NuSol.CUDA as NuC
from Checks import *
from NeutrinoSolutionDeconstruct import *
from time import time

def ParticleCollectors(ev):
    t1 = [ t for t in ev.Tops if t.LeptonicDecay][0]
    t2 = [ t for t in ev.Tops if t.LeptonicDecay][1]
    
    out = []
    prt = { abs(p.pdgid) : p for p in t1.Children }
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    out.append([b, lep, nu, t1])
    
    prt = { abs(p.pdgid) : p for p in t2.Children }
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    out.append([b, lep, nu, t2])

    return out

Ana = Analysis()
Ana.InputSample("bsm4t-1000")
Ana.Event = Event
Ana.EventStop = 100
Ana.EventCache = True
Ana.DumpPickle = True 
Ana.chnk = 100
Ana.Launch()

it = 0
vl = {"b" : [], "lep" : [], "nu" : [], "ev" : [], "t" : []}
for i in Ana:
    ev = i.Trees["nominal"]
    tops = [ t for t in ev.Tops if t.LeptonicDecay]

    if len(tops) == 2:
        k = ParticleCollectors(ev)
        vl["b"].append(  [k[0][0], k[1][0]])
        vl["lep"].append([k[0][1], k[1][1]])
        vl["nu"].append( [k[0][2], k[1][2]])
        vl["t"].append(  [k[0][3], k[1][3]])
        vl["ev"].append(ev)

T = SampleTensor(vl["b"], vl["lep"], vl["ev"], vl["t"], "cuda")
R = SampleVector(vl["b"], vl["lep"], vl["ev"], vl["t"])

NuT.Nu(T.b, T.mu, T.mT, T.mW, T.mN)

t1 = time()
t_sol = NuT.Nu(T.b, T.mu, T.mT, T.mW, T.mN)
diff1 = time() - t1 

t1 = time()
t_solC = NuC.Nu(T.b, T.mu, T.mT, T.mW, T.mN)
diff2 = time() - t1

print(t_sol[0])
print(t_solC[0])
print(AssertEquivalenceRecursive(t_sol.tolist(), t_solC.tolist()))
print("--- Testing Performance Between C++ and CUDA of Rz ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)


exit()
for r, t in zip(R, T):
    b, mu = r[0], r[1]
    _b, _mu = r[2], r[3]
    met_x, met_y = r[4], r[5]
    mT, mW, mNu = r[6], r[7], r[8]
   
    tb_, tmu_ = t[0], t[1]
    t_b_, t_mu_ = t[2], t[3]
    t_met, t_phi = t[4], t[5]
    t_mT, t_mW, t_mNu = t[6], t[7], t[8]
    
    # Test if the Solution values are identical up to 0.0001%
    t_sol = NuT.Solutions(tb_, tmu_, t_mT, t_mW, t_mNu)
    s = SolutionSet(b, mu, mW**2, mT**2, mNu**2)
    
    sol = torch.tensor([[s.c, s.s, s.x0, s.x0p, s.Sx, s.Sy, 
                         s.w, s.w_, s.x1, s.y1, s.Z, s.Om2, 
                         s.eps2]], device = "cuda")
    AssertEquivalenceRecursive(sol, t_sol, 0.0001)
    
    # Testing the Single Neutrino 
    t_sol = NuT.Nu(tb_, tmu_, t_mT, t_mW, t_mNu)

    print(s.H)
    print(t_sol)

    AssertEquivalenceRecursive(s.H, t_sol.tolist()[0], 0.0001)

    exit()
