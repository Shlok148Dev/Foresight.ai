import pytest
from app.services.anomaly_detection import AnomalyDetector

def test_anomaly_detection():
    detector = AnomalyDetector()
    
    # Normal history
    history = [
        {"timestamp": f"2026-05-{10+i}", "count": 10 + i * 2}
        for i in range(10)
    ]
    
    result = detector.detect_anomalies(history)
    assert "is_anomaly" in result
    assert "anomaly_score" in result
    assert "anomaly_type" in result
    assert "confidence" in result

    # Anomalous history (sudden spike)
    anomalous_history = [
        {"timestamp": f"2026-05-{10+i}", "count": 10 + i * 2}
        for i in range(9)
    ] + [{"timestamp": "2026-05-19", "count": 500}]
    
    anomaly_result = detector.detect_anomalies(anomalous_history)
    assert "is_anomaly" in anomaly_result
