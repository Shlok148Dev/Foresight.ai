"""
Foresight — MiroFish Integration
=================================
Phase 2F: Multi-agent trend simulation and virality prediction.
"""

from typing import Dict, List
import math

class MiroFishSimulator:
    def __init__(self):
        self.communities = self._initialize_communities()
    
    def _initialize_communities(self) -> Dict:
        """Initialize simulation communities."""
        return {
            "reddit_tech": {
                "name": "r/Technology",
                "platform": "reddit",
                "size": 5000000,
                "influence": 0.8,
                "adoption_rate": 0.3
            },
            "twitter_tech": {
                "name": "Twitter Tech",
                "platform": "twitter",
                "size": 2000000,
                "influence": 0.9,
                "adoption_rate": 0.4
            },
            "discord_dev": {
                "name": "Discord Dev",
                "platform": "discord",
                "size": 500000,
                "influence": 0.7,
                "adoption_rate": 0.5
            },
            "hackernews": {
                "name": "Hacker News",
                "platform": "hackernews",
                "size": 1000000,
                "influence": 0.95,
                "adoption_rate": 0.2
            },
            "mainstream_media": {
                "name": "Mainstream Media",
                "platform": "news",
                "size": 100000000,
                "influence": 1.0,
                "adoption_rate": 0.1
            }
        }
    
    def simulate_trend_spread(self, signal: Dict, days: int = 21) -> Dict:
        """Simulate trend spread over time."""
        simulation = {
            "signal_id": signal.get("id"),
            "timeline": [],
            "virality_coefficient": 0.0,
            "mainstream_eta": None
        }
        
        # Simulate day by day
        for day in range(days):
            day_data = {
                "day": day,
                "communities": {}
            }
            
            for community_id, community in self.communities.items():
                adoption = self._calculate_adoption(
                    community,
                    day,
                    signal.get("confidence", 50)
                )
                day_data["communities"][community_id] = adoption
            
            simulation["timeline"].append(day_data)
        
        simulation["virality_coefficient"] = self._calculate_virality(simulation)
        simulation["mainstream_eta"] = self._predict_mainstream_eta(simulation)
        
        return simulation
    
    def _calculate_adoption(self, community: Dict, day: int, confidence: int) -> float:
        """Calculate adoption rate using an S-curve (sigmoid)."""
        base_rate = community["adoption_rate"]
        influence = community["influence"]
        confidence_factor = confidence / 100.0
        
        # Sigmoid function for S-curve adoption
        adoption = base_rate * influence * confidence_factor * (1 / (1 + math.exp(-day + 10)))
        return min(adoption, 1.0)
    
    def _calculate_virality(self, simulation: Dict) -> float:
        """Calculate overall virality coefficient across all days."""
        total_adoption = 0.0
        timeline = simulation["timeline"]
        for day_data in timeline:
            for adoption in day_data["communities"].values():
                total_adoption += adoption
        
        if not timeline:
            return 0.0
        return total_adoption / len(timeline)
    
    def _predict_mainstream_eta(self, simulation: Dict) -> int | None:
        """Predict day when trend reaches mainstream (>50% adoption)."""
        for day_idx, day_data in enumerate(simulation["timeline"]):
            mainstream_adoption = day_data["communities"].get("mainstream_media", 0)
            if mainstream_adoption > 0.5:
                return day_idx
        return None

# Singleton instance
mirofish_simulator = MiroFishSimulator()
