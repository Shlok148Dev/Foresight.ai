import pytest
import numpy as np
from app.services.advanced_clustering import AdvancedClusteringEngine

def test_advanced_clustering():
    engine = AdvancedClusteringEngine(embedding_dim=4)
    
    # Generate mock signals
    # Cluster 1
    signals = [{"id": i, "embedding": np.array([1.0, 1.0, 0.0, 0.0]) + np.random.normal(0, 0.1, 4)} for i in range(10)]
    # Cluster 2
    signals += [{"id": i+10, "embedding": np.array([0.0, 0.0, 1.0, 1.0]) + np.random.normal(0, 0.1, 4)} for i in range(10)]
    
    result = engine.cluster_signals(signals)
    
    assert "clusters" in result
    assert "noise_points" in result
    assert result["num_clusters"] >= 2
    assert "cluster_quality" in result

def test_similarity_search():
    engine = AdvancedClusteringEngine(embedding_dim=4)
    signals = [{"id": i, "embedding": np.array([1.0, 1.0, 0.0, 0.0]) + np.random.normal(0, 0.1, 4)} for i in range(5)]
    engine.cluster_signals(signals)
    
    query = np.array([1.0, 1.0, 0.0, 0.0])
    indices = engine.find_similar_signals(query, k=2)
    assert len(indices) == 2
