import pytest
import numpy as np
from app.services.forecasting_ensemble import EnsembleForecaster

def test_ensemble_forecasting():
    forecaster = EnsembleForecaster()
    
    history = [
        {"timestamp": "2026-05-20", "count": 10},
        {"timestamp": "2026-05-21", "count": 15},
        {"timestamp": "2026-05-22", "count": 25},
        {"timestamp": "2026-05-23", "count": 40},
        {"timestamp": "2026-05-24", "count": 65},
    ]
    
    result = forecaster.forecast_trend(history, periods=7)
    
    assert "forecast" in result
    assert "virality_score" in result
    assert "peak_day" in result
    assert "mainstream_eta" in result
    assert len(result["forecast"]) == 7
    assert 0 <= result["virality_score"] <= 100
    assert len(result["models_used"]) >= 1  # At least one model succeeds

def test_virality_calculation():
    forecaster = EnsembleForecaster()
    
    history = [
        {"timestamp": "2026-05-20", "count": 10},
        {"timestamp": "2026-05-21", "count": 20},
        {"timestamp": "2026-05-22", "count": 30},
    ]
    
    forecast = np.array([50, 100, 150, 200, 250])
    virality = forecaster._calculate_virality(forecast, history)
    
    assert virality > 50  # High growth
