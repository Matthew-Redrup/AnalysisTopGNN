from torch_geometric.nn import MessagePassing, GCNConv, TopKPooling
from torch_geometric.data import Batch 
import torch.nn.functional as F
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid
from skhep.math.vectors import LorentzVector
from torch_scatter import scatter
import torch 
import math
from itertools import combinations

class EdgeConv(MessagePassing):

    def __init__(self, in_channels, out_channels):
        super(EdgeConv, self).__init__(aggr = "mean") 
        self.mlp = Seq(Linear(2 * in_channels, out_channels), Sigmoid(), Linear(out_channels, out_channels))
    
    def forward(self, sample):
        x, edge_index = sample.x, sample.edge_index
        return self.propagate(edge_index, x = x)

    def message(self, x_i, x_j):
        tmp = torch.cat([x_i, x_j - x_i], dim = 1)
        return self.mlp(tmp)

    def update(self, aggr_out):
        return F.normalize(aggr_out)

class GCN(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super(GCN, self).__init__()
        self.conv1 = GCNConv(in_channels, 16)
        self.conv2 = GCNConv(16, out_channels)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, training = self.training)
        x = self.conv2(x, edge_index)

        return F.log_softmax(x, dim = 1)

class InvMassGNN(MessagePassing):

    def __init__(self, out_channels):
        super(InvMassGNN, self).__init__(aggr = "add")
        #self.mlp = Seq(Linear(6, 6), ReLU(), Linear(6, 64), ReLU(), Linear(64, 64), ReLU(), Linear(64, out_channels))
        self.mlp = Seq(Linear(6, 32), ReLU(), Linear(32, 128), ReLU(), Linear(128, 64), ReLU(), Linear(64, out_channels))
    def forward(self, data):

        # Kinematics 
        e, pt, eta, phi = data.e, data.pt, data.eta, data.phi
        edge_index = data.edge_index
        x = torch.cat([e, pt, eta, phi], dim = 1)

        return self.propagate(edge_index, x = x, dr = data.dr, m = data.m) 

    def message(self, x_i, x_j, dr, m):
        return self.mlp(torch.cat([x_i, dr, m], dim = 1))

    def update(self, aggr_out):
        return F.normalize(aggr_out)
        


class InvMassAggr(MessagePassing):

    def __init__(self, out_channels):
        super(InvMassAggr, self).__init__(aggr = "add")
        self.mlp = Seq(Linear(8 +2, 64), ReLU(), Linear(64, 64), ReLU(), Linear(64, 63))
        self.Mmlp = Seq(Linear(63 + 1, 63 + 1), ReLU(), Linear(63+1, out_channels))
    def forward(self, data):

        # Kinematics 
        e, pt, eta, phi = data.e, data.pt, data.eta, data.phi
        x = torch.cat([data.e, data.pt, data.eta, data.phi], dim = 1)
        return self.propagate(edge_index = data.edge_index, x = x, dr = data.dr, m = data.m, y = data.y) 

    def message(self, x_i, x_j):
        dr = []
        m = []
        de = []
        for i, j in zip(x_i, x_j):
            del_R = math.sqrt(math.pow(i[2] - j[2], 2) + math.pow(i[3] - j[3], 2))
            dr.append([del_R])
            T_i = LorentzVector()
            T_i.setptetaphie(i[1], i[2], i[3], i[0])

            T_j = LorentzVector()
            T_j.setptetaphie(j[1], j[2], j[3], j[0])
            T = T_j + T_i
            m.append([T.mass])
        
        dr = torch.tensor(dr)
        m = torch.tensor(m)
        dr = torch.cat([x_i, dr, m, abs(x_i - x_j)], dim = 1)
        return self.mlp(dr)
    
    def aggregate(self, inputs, index, dim_size):
        #https://pytorch-scatter.readthedocs.io/en/latest/functions/scatter.html
        # - Basically a form of hashing where the index is used to extract values from the inputs and sums these values @ index value
        return scatter(inputs, index, dim = self.node_dim, dim_size = dim_size, reduce = "add")

    def update(self, aggr_out, x, edge_index, y):
        #aggr_out = F.normalize(aggr_out)
        #edge_weight = torch.sigmoid(torch.matmul(aggr_out, aggr_out.t()))

        #print(aggr_out)
        #print(edge_weight) 
        
        _, p = aggr_out.max(1)
        M = [LorentzVector() for i in range(len(x))]
        for e_i, e_j in zip(edge_index[0], edge_index[1]):
            # incoming kinematic quantities  x_j -> x_i            
            #if edge_weight[e_j][e_i] > self.Threshold:
            
            if p[e_i] == p[e_j]:
                v = LorentzVector()
                v.setptetaphie(x[e_j][1], x[e_j][2], x[e_j][3], x[e_j][0])
                M[e_i]+=v
        
        # Include own mass in the calculation
        for e_i in set(edge_index[0].tolist()):
            v = LorentzVector()
            v.setptetaphie(x[e_i][1], x[e_i][2], x[e_i][3], x[e_i][0])
            M[e_i] += v

        M = torch.cat([aggr_out, torch.tensor([[i.mass] for i in M])], dim = 1)
        return F.normalize(self.Mmlp(F.normalize(M)))


class PathNets(MessagePassing):
    
    def __init__(self, out_channels, debug = False):
        super(PathNets, self).__init__(aggr = "add")
        self.mlp = Seq(Linear(8, 64), ReLU(), Linear(64, 64), ReLU(), Linear(64,4))
        self.mlp_path = Seq(Linear(1, 10), ReLU(), Linear(10, 10), ReLU(), Linear(10, 1))
        
        self.Debug = debug
        if self.Debug:
            self.Debug_L = []

    def forward(self, data): 
        x = torch.cat([data.e, data.pt, data.eta, data.phi], dim = 1)
        edge_attr, edge_index = torch.cat([data.dr, data.m], dim = 1), data.edge_index
        d = edge_index.device
        
        Path = []
        Path_mass = []
        unique = torch.unique(edge_index)
        for k in range(1, len(torch.unique(unique))):
            P = torch.tensor(list(combinations(unique, k+1)))
            for s_gr in P:
                v = True
                for ed in range(len(s_gr)-1):
                    if torch.tensor([s_gr[ed], s_gr[ed+1]], device = d) in edge_index.t():
                        pass
                    else:
                        v = False
                        break
                if v:
                    Path.append(s_gr)
                    Path_mass.append(LorentzVector())
                    
                    for i in x[s_gr]:
                        tmp_v = LorentzVector()
                        tmp_v.setptetaphie(i[1], i[2], i[3], i[0])
                        Path_mass[len(Path)-1] += tmp_v
                    Path_mass[len(Path)-1] = [Path_mass[len(Path)-1].mass]
        
        
        if self.Debug:
            self.Debug_L = [Path_mass, Path]

        Path_prob = F.normalize(self.mlp_path(torch.tensor(Path_mass, device = d)))
        Aggr_Edge_P = torch.zeros(edge_index.shape[1], 1, device = d)
    
        # Aggregate the path probability into segmented edge scores 
        edge_T = edge_index.t().tolist()
        for s_gr, p in zip(Path, Path_prob):
            for k in s_gr.unfold(0, 2, 1):
                ix = edge_T.index(k.tolist())
                Aggr_Edge_P[ix] *= p[0]
        
        print(Aggr_Edge_P.t(), edge_index)
        edge_attr = torch.cat([edge_attr, Aggr_Edge_P], dim = 1)
        return self.propagate(edge_index = edge_index, x = x, edge_attr = edge_attr)

    def message(self, edge_index, x_i, x_j, edge_attr):
         
        tmp = torch.cat([x_i, abs(x_j[:, 3:4] - x_i[:, 3:4]), edge_attr], dim = 1)
        return self.mlp(tmp)

    def update(self, aggr_out):
        return F.normalize(aggr_out)
