def Comparison(a, b, key = None):
    
    same = False
    try:
        if a == b: 
            return True
        if round(float(a)/float(b), 4) == 1.0:
            return True
    except:
        same = False
    
    try: 
        import torch
        if torch.all( a == b):
            return True 
    except:
        same = False
    
    try:
        if len(a) != len(b):
            print("!!!! ", a, b)
            return False
        for i, j in zip(a, b):
            if j == i:
                continue
            if round(float(j)/float(i), 4) == 1.0:
                continue
            print("####> ", float(i), "  |||   ", float(j), type(a), key, "  |||   ", round(float(j)/float(i), 4))
            return False
        return True
    except:
        same = False
    print(a, b)
    return same

def ObjectIter(a, b):
    try:
        assert a.__dict__.keys() == b.__dict__.keys()
    except:
        print("!!!!! -> ", a.__dict__.keys(), "  |||  ",  b.__dict__.keys())
        return False

    for i in a.__dict__.keys():
        CompareObjects(a.__dict__[i], b.__dict__[i], i)
    return True

def DictIter(a, b, key):
    assert len(a) == len(b)
    for i, j in zip(sorted(a), sorted(b)):
        try:
            assert i == j
            assert CompareObjects(a[i], b[j], i) == True
        except:
            print(CompareObjects(a[i], b[j], i))
            print("Dictionary !!! -> ", i, "  |||  ", j, "   ", len(a), len(b), key)
            return False
        
    return True 

def ListIter(a, b):
    assert len(a) == len(b)
    for i, j in zip(a, b):
        try:
            assert i == j
            assert CompareObjects(i, j) == True
        except:
            print("List !!! -> ", i, "  |||  ", j, "   ", len(a), len(b))
            return False
    return True 

def CompareObjects(obj1, obj2, key = None):
  
    if type(obj1).__name__ == "function": 
        return True
    if type(obj2).__name__ == "function":
        return True
    
    try:
        assert type(obj1) == type(obj2)
    except assertion: 
        print(type(obj1), type(obj2), obj1, obj2, key)


    if type(obj1).__name__ == "GenerateDataLoader":
        return ObjectIter(obj1, obj2)

    elif type(obj1).__name__ == "EventGenerator":
        return ObjectIter(obj1, obj2)

    elif type(obj1).__name__ == "Event":
        return ObjectIter(obj1, obj2)
    
    elif "Particles" in type(obj1).__module__:
        return ObjectIter(obj1, obj2)

    elif type(obj1).__name__ == "Data":
        return CompareObjects(obj1.to_dict(), obj2.to_dict())

    elif type(obj1).__name__ == "torch":
         return ObjectIter(obj1, obj2)

    elif isinstance(obj1, list):
        return ListIter(obj1, obj2)

    elif isinstance(obj1, dict):
        return DictIter(obj1, obj2, key)
    
    out = Comparison(obj1, obj2, key)
    if out:
        return True
    else:
        print(" =================================> " + str(key))
        print("!!! --> ", obj1, obj2, type(obj1), type(obj2))
        return False


def CacheEventGenerator(Stop, Dir, Name, Cache):
    from Functions.IO.IO import UnpickleObject, PickleObject   
    from Functions.Event.EventGenerator import EventGenerator

    if Cache:
        ev = EventGenerator(Dir, Stop = Stop)
        ev.SpawnEvents()
        ev.CompileEvent(SingleThread = False)
        PickleObject(ev, Name) 
    return UnpickleObject(Name)


def CreateEventGeneratorComplete(Stop, Files, Name, CreateCache, NameOfCaller):
    from Functions.IO.IO import UnpickleObject, PickleObject   
    from Functions.Event.EventGenerator import EventGenerator 

    out = []
    for i, j in zip(Files, Name):
        if CreateCache:
            ev = EventGenerator(i, Stop = Stop)
            ev.SpawnEvents()
            ev.CompileEvent(SingleThread = False)
            PickleObject(ev, j, Dir = "_Pickle/" +  NameOfCaller) 
        out.append(UnpickleObject(j, Dir = "_Pickle/" + NameOfCaller))
    return out

def CreateDataLoaderComplete(Files, Level, Name, CreateCache, NameOfCaller = None):
    from Functions.IO.IO import UnpickleObject, PickleObject   
    if CreateCache:

        import Functions.FeatureTemplates.EdgeFeatures as ef
        import Functions.FeatureTemplates.NodeFeatures as nf
        import Functions.FeatureTemplates.GraphFeatures as gf
        from Functions.Event.DataLoader import GenerateDataLoader

        DL = GenerateDataLoader()

        # Edge Features 
        DL.AddEdgeFeature("dr", ef.d_r)
        DL.AddEdgeFeature("mass", ef.mass)       
        DL.AddEdgeFeature("signal", ef.Signal)
 
        # Node Features 
        DL.AddNodeFeature("eta", nf.eta)
        DL.AddNodeFeature("pt", nf.pt)       
        DL.AddNodeFeature("phi", nf.phi)      
        DL.AddNodeFeature("energy", nf.energy)
        DL.AddNodeFeature("signal", nf.Signal)
        
        # Graph Features 
        DL.AddGraphFeature("mu", gf.Mu)
        DL.AddGraphFeature("m_phi", gf.MissingPhi)       
        DL.AddGraphFeature("m_et", gf.MissingET)      
        DL.AddGraphFeature("signal", gf.Signal)       


        # Truth Stuff 
        DL.AddEdgeTruth("Topology", ef.Signal)
        DL.AddNodeTruth("Index", nf.Index)
        DL.AddNodeTruth("NodeSignal", nf.Signal)
        DL.AddGraphTruth("GraphMuActual", gf.MuActual)
        DL.AddGraphTruth("GraphEt", gf.MissingET)
        DL.AddGraphTruth("GraphPhi", gf.MissingPhi)
        DL.AddGraphTruth("GraphSignal", gf.Signal)

        DL.SetDevice("cuda")
        for i in Files:
            if NameOfCaller != None:
                ev = UnpickleObject(NameOfCaller + "/" + i)
            else:
                ev = UnpickleObject(i + "/" + i)

            DL.AddSample(ev, "nominal", Level, True, True)
        if NameOfCaller == None:
            DL.MakeTrainingSample(20)

        PickleObject(DL, Name)
    return UnpickleObject(Name)






