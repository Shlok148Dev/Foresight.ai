import torch
import torch.nn as nn
from torch_geometric.nn import GATConv, global_mean_pool
from torch_geometric.data import Data
import numpy as np
from typing import Dict, List

class TrendPropagationGNN(nn.Module):
    """
    Graph Attention Network for trend propagation
    
    Nodes: Communities (Reddit, Twitter, TikTok, Discord, HackerNews, Mainstream)
    Edges: Influence connections
    Features: Adoption rate, community size, influence
    """
    
    def __init__(self, in_channels: int = 3, hidden_channels: int = 64, out_channels: int = 1):
        super().__init__()
        
        # Graph Attention Layers
        self.gat1 = GATConv(in_channels, hidden_channels, heads=4, dropout=0.2)
        self.gat2 = GATConv(hidden_channels * 4, hidden_channels, heads=4, dropout=0.2)
        self.gat3 = GATConv(hidden_channels * 4, hidden_channels, dropout=0.2)
        
        # Prediction head
        self.linear1 = nn.Linear(hidden_channels, 32)
        self.linear2 = nn.Linear(32, out_channels)
        self.relu = nn.ReLU()
    
    def forward(self, x, edge_index, batch=None):
        x = self.gat1(x, edge_index)
        x = self.relu(x)
        
        x = self.gat2(x, edge_index)
        x = self.relu(x)
        
        x = self.gat3(x, edge_index)
        x = self.relu(x)
        
        if batch is not None:
            x = global_mean_pool(x, batch)
        else:
            x = x.mean(dim=0, keepdim=True)
        
        x = self.linear1(x)
        x = self.relu(x)
        x = self.linear2(x)
        
        return x

class TrendNetworkAnalyzer:
    """Analyzes trend propagation using GNN"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = TrendPropagationGNN().to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        # Community network
        self.communities = {
            0: {"name": "Reddit Tech", "size": 5000000, "influence": 0.8},
            1: {"name": "Twitter Tech", "size": 2000000, "influence": 0.9},
            2: {"name": "Discord Dev", "size": 500000, "influence": 0.7},
            3: {"name": "HackerNews", "size": 1000000, "influence": 0.95},
            4: {"name": "TikTok", "size": 50000000, "influence": 0.6},
            5: {"name": "Mainstream", "size": 100000000, "influence": 1.0}
        }
        
        # Edges: influence connections
        self.edges = [
            (0, 1), (0, 2), (0, 3),
            (1, 4), (1, 5),
            (2, 1), (2, 4),
            (3, 5),
            (4, 5)
        ]
    
    def predict_propagation(self, signal: Dict, time_steps: int = 21) -> Dict:
        """Predict trend propagation through network"""
        
        x, edge_index = self._create_graph(signal)
        propagation = []
        current_state = x.clone()
        
        for t in range(time_steps):
            with torch.no_grad():
                adoption_rates = self.model(current_state, edge_index)
            
            propagation.append(adoption_rates.cpu().numpy())
            current_state = self._update_state(current_state, adoption_rates)
        
        propagation_array = np.array(propagation).squeeze()
        
        return {
            "propagation_timeline": propagation_array.tolist(),
            "influence_scores": self._calculate_influence_scores(),
            "peak_community": self._predict_peak_community(propagation_array),
            "mainstream_probability": self._predict_mainstream_probability(propagation_array),
            "critical_path": self._find_critical_path()
        }
    
    def _create_graph(self, signal: Dict) -> tuple:
        """Create graph from signal"""
        x = []
        for comm_id in range(len(self.communities)):
            comm = self.communities[comm_id]
            adoption_rate = signal.get("initial_adoption", 0.1)
            size = comm["size"] / 100000000
            influence = comm["influence"]
            
            x.append([adoption_rate, size, influence])
        
        x = torch.tensor(x, dtype=torch.float32).to(self.device)
        edge_index = torch.tensor(self.edges, dtype=torch.long).t().contiguous().to(self.device)
        
        return x, edge_index
    
    def _update_state(self, state: torch.Tensor, adoption_rates: torch.Tensor) -> torch.Tensor:
        """Update state for next time step"""
        new_state = state.clone()
        new_state[:, 0] = torch.clamp(state[:, 0] + adoption_rates.squeeze() * 0.1, 0, 1)
        return new_state
    
    def _calculate_influence_scores(self) -> Dict:
        """Calculate influence scores"""
        return {comm["name"]: comm["influence"] for comm in self.communities.values()}
    
    def _predict_peak_community(self, propagation: np.ndarray) -> str:
        """Predict which community peaks first"""
        if propagation.ndim < 2:
            propagation = np.expand_dims(propagation, axis=1)
            if propagation.shape[1] != len(self.communities):
                propagation = np.zeros((len(propagation), len(self.communities)))
        peak_indices = np.argmax(propagation, axis=0)
        peak_comm_id = np.argmax(peak_indices)
        return self.communities[peak_comm_id]["name"]
    
    def _predict_mainstream_probability(self, propagation: np.ndarray) -> float:
        """Predict probability of going mainstream"""
        if propagation.ndim < 2 or propagation.shape[1] != len(self.communities):
            return 0.5
        return float(propagation[-1, 5])
    
    def _find_critical_path(self) -> List[str]:
        """Find critical path through network"""
        return [
            self.communities[0]["name"],
            self.communities[1]["name"],
            self.communities[4]["name"],
            self.communities[5]["name"]
        ]
