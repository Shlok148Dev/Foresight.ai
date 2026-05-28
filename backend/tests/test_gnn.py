import pytest
from app.services.graph_neural_networks import TrendNetworkAnalyzer

def test_gnn_propagation():
    # Wrap in try/except because torch dll might fail on some windows setups
    try:
        analyzer = TrendNetworkAnalyzer()
        
        signal = {
            "id": "trend_123",
            "initial_adoption": 0.1,
            "confidence": 75
        }
        
        result = analyzer.predict_propagation(signal, time_steps=21)
        
        assert "propagation_timeline" in result
        assert "influence_scores" in result
        assert "peak_community" in result
        assert "mainstream_probability" in result
        assert len(result["propagation_timeline"]) == 21
        assert 0 <= result["mainstream_probability"] <= 1
    except (OSError, ImportError) as e:
        pytest.skip(f"Skipping test due to torch/DLL setup issues: {e}")
