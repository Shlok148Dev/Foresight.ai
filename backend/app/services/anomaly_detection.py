from sklearn.ensemble import IsolationForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
import numpy as np
from typing import List, Dict

class AnomalyDetector:
    """Detects anomalous trend patterns"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.knn = KNN(contamination=0.1)
        self.lof = LOF(contamination=0.1)
        
        # Fit models on dummy data to initialize them for single predictions
        # (In production, these would be fit on historical trend data)
        dummy_data = np.random.randn(100, 6)
        self.isolation_forest.fit(dummy_data)
        self.knn.fit(dummy_data)
        self.lof.fit(dummy_data)
    
    def detect_anomalies(self, signal_history: List[Dict]) -> Dict:
        """Detect anomalies in trend history"""
        if len(signal_history) < 6:
            # Need at least 6 points to compute features safely
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "anomaly_type": None,
                "confidence": 0.0
            }
        
        features = self._extract_features(signal_history)
        
        # Ensemble anomaly detection
        try:
            if_score = self.isolation_forest.decision_function(features)
            knn_score = self.knn.decision_function(features)
            lof_score = self.lof.decision_function(features)
            
            # Ensemble: average
            ensemble_score = np.mean([if_score, knn_score, lof_score])
            
            is_anomaly = ensemble_score < -0.5
            anomaly_type = self._classify_anomaly_type(signal_history) if is_anomaly else None
            
            return {
                "is_anomaly": bool(is_anomaly),
                "anomaly_score": float(ensemble_score),
                "anomaly_type": anomaly_type,
                "confidence": float(np.abs(ensemble_score))
            }
        except Exception:
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "anomaly_type": None,
                "confidence": 0.0
            }
    
    def _extract_features(self, signal_history: List[Dict]) -> np.ndarray:
        """Extract features for anomaly detection"""
        counts = np.array([s["count"] for s in signal_history])
        
        features = np.array([
            np.mean(counts),
            np.std(counts),
            np.max(counts),
            np.min(counts),
            np.mean(np.diff(counts)),
            np.mean(np.diff(np.diff(counts)))
        ]).reshape(1, -1)
        
        return features
    
    def _classify_anomaly_type(self, signal_history: List[Dict]) -> str:
        """Classify type of anomaly"""
        counts = np.array([s["count"] for s in signal_history])
        recent = counts[-5:]
        
        if recent[-1] > np.mean(counts) * 3:
            return "sudden_spike"
        
        if np.std(recent) < np.mean(counts) * 0.1:
            return "unusual_plateau"
        
        if np.mean(np.diff(recent)) < -np.mean(counts) * 0.2:
            return "rapid_decline"
        
        return "unknown"
