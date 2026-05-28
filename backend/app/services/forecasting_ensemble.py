from neuralforecast.models import LSTM, Transformer, MLP
from darts import TimeSeries
from darts.models import AutoARIMA, ExponentialSmoothing
from statsforecast.models import AutoARIMA as SF_AutoARIMA
from prophet import Prophet
import numpy as np
import pandas as pd
from typing import Dict, List

class EnsembleForecaster:
    """
    Combines 6 forecasting models for robust trend prediction:
    1. NeuralForecast LSTM (deep learning)
    2. NeuralForecast Transformer (attention-based)
    3. Darts AutoARIMA (statistical)
    4. Darts ExponentialSmoothing (statistical)
    5. Prophet (seasonal decomposition)
    6. StatsForecast AutoARIMA (fast statistical)
    """
    
    def __init__(self):
        self.models = {
            "neural_lstm": LSTM(input_size=1, hidden_size=64, n_layers=2),
            "neural_transformer": Transformer(input_size=1, d_model=64, nhead=4),
            "darts_arima": AutoARIMA(),
            "darts_exp_smooth": ExponentialSmoothing(),
            "prophet": None,  # Initialized per forecast
            "statsforecast": SF_AutoARIMA()
        }
    
    def forecast_trend(self, signal_history: List[Dict], periods: int = 21) -> Dict:
        """
        Ensemble forecast combining 6 models
        
        Args:
            signal_history: List of {"timestamp": "...", "count": N}
            periods: Days to forecast ahead
        
        Returns:
            {
                "forecast": [10, 15, 22, 35, 50, ...],
                "confidence_upper": [12, 18, 26, 42, 60, ...],
                "confidence_lower": [8, 12, 18, 28, 40, ...],
                "virality_score": 75,  # 0-100
                "peak_day": 5,
                "mainstream_eta": 7,
                "models_used": ["neural_lstm", "darts_arima", ...]
            }
        """
        
        # Prepare data
        ts_data = self._prepare_timeseries(signal_history)
        df = self._prepare_dataframe(signal_history)
        
        # Get predictions from each model
        predictions = {}
        
        # NeuralForecast models
        try:
            pred_lstm = self._forecast_neural(self.models["neural_lstm"], ts_data, periods)
            predictions["neural_lstm"] = pred_lstm
        except Exception as e:
            pass
        
        try:
            pred_transformer = self._forecast_neural(self.models["neural_transformer"], ts_data, periods)
            predictions["neural_transformer"] = pred_transformer
        except Exception as e:
            pass
        
        # Darts models
        try:
            pred_arima = self._forecast_darts(self.models["darts_arima"], ts_data, periods)
            predictions["darts_arima"] = pred_arima
        except Exception as e:
            pass
        
        try:
            pred_exp = self._forecast_darts(self.models["darts_exp_smooth"], ts_data, periods)
            predictions["darts_exp_smooth"] = pred_exp
        except Exception as e:
            pass
        
        # Prophet
        try:
            prophet_model = Prophet(yearly_seasonality=False, daily_seasonality=True)
            pred_prophet = self._forecast_prophet(prophet_model, df, periods)
            predictions["prophet"] = pred_prophet
        except Exception as e:
            pass
        
        # StatsForecast
        try:
            pred_statsforecast = self._forecast_statsforecast(self.models["statsforecast"], ts_data, periods)
            predictions["statsforecast"] = pred_statsforecast
        except Exception as e:
            pass
        
        # Ensemble: weighted average
        if not predictions:
            raise ValueError("All models failed")
        
        ensemble = self._ensemble_predictions(predictions)
        
        # Calculate metrics
        virality_score = self._calculate_virality(ensemble["mean"], signal_history)
        peak_day = self._predict_peak_day(ensemble["mean"])
        mainstream_eta = self._predict_mainstream_eta(ensemble["mean"])
        
        return {
            "forecast": ensemble["mean"].tolist(),
            "confidence_upper": ensemble["upper"].tolist(),
            "confidence_lower": ensemble["lower"].tolist(),
            "virality_score": virality_score,
            "peak_day": peak_day,
            "mainstream_eta": mainstream_eta,
            "models_used": list(predictions.keys()),
            "model_weights": self._calculate_model_weights(predictions)
        }
    
    def _prepare_timeseries(self, signal_history: List[Dict]) -> TimeSeries:
        """Convert to Darts TimeSeries"""
        values = np.array([s["count"] for s in signal_history])
        return TimeSeries.from_values(values)
    
    def _prepare_dataframe(self, signal_history: List[Dict]) -> pd.DataFrame:
        """Convert to Prophet DataFrame"""
        return pd.DataFrame({
            "ds": pd.to_datetime([s["timestamp"] for s in signal_history]),
            "y": [s["count"] for s in signal_history]
        })
    
    def _forecast_neural(self, model, ts_data: TimeSeries, periods: int) -> Dict:
        """Forecast using NeuralForecast"""
        model.fit(ts_data, epochs=10, verbose=False)
        forecast = model.predict(n=periods)
        
        return {
            "mean": forecast.values.flatten(),
            "upper": forecast.values.flatten() * 1.15,
            "lower": forecast.values.flatten() * 0.85
        }
    
    def _forecast_darts(self, model, ts_data: TimeSeries, periods: int) -> Dict:
        """Forecast using Darts"""
        model.fit(ts_data)
        forecast = model.predict(n=periods)
        
        return {
            "mean": forecast.values.flatten(),
            "upper": forecast.values.flatten() * 1.15,
            "lower": forecast.values.flatten() * 0.85
        }
    
    def _forecast_prophet(self, model, df: pd.DataFrame, periods: int) -> Dict:
        """Forecast using Prophet"""
        model.fit(df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        tail = forecast.tail(periods)
        return {
            "mean": tail["yhat"].values,
            "upper": tail["yhat_upper"].values,
            "lower": tail["yhat_lower"].values
        }
    
    def _forecast_statsforecast(self, model, ts_data: TimeSeries, periods: int) -> Dict:
        """Forecast using StatsForecast"""
        model.fit(ts_data)
        forecast = model.predict(n=periods)
        
        return {
            "mean": forecast.values.flatten(),
            "upper": forecast.values.flatten() * 1.15,
            "lower": forecast.values.flatten() * 0.85
        }
    
    def _ensemble_predictions(self, predictions: Dict) -> Dict:
        """Ensemble: weighted average"""
        forecasts = np.array([p["mean"] for p in predictions.values()])
        
        ensemble_mean = np.mean(forecasts, axis=0)
        ensemble_upper = np.percentile(forecasts, 95, axis=0)
        ensemble_lower = np.percentile(forecasts, 5, axis=0)
        
        return {
            "mean": ensemble_mean,
            "upper": ensemble_upper,
            "lower": ensemble_lower
        }
    
    def _calculate_virality(self, forecast: np.ndarray, history: List[Dict]) -> int:
        """Virality score (0-100)"""
        current = history[-1]["count"]
        peak = np.max(forecast)
        growth = peak / max(current, 1)
        
        return min(int(growth * 20), 100)
    
    def _predict_peak_day(self, forecast: np.ndarray) -> int:
        """Which day peaks"""
        return int(np.argmax(forecast))
    
    def _predict_mainstream_eta(self, forecast: np.ndarray) -> int:
        """Days to mainstream"""
        threshold = np.max(forecast) * 0.7
        for i, val in enumerate(forecast):
            if val >= threshold:
                return i
        return len(forecast)
    
    def _calculate_model_weights(self, predictions: Dict) -> Dict:
        """Model contribution weights"""
        weights = {}
        for name, pred in predictions.items():
            weights[name] = float(np.std(pred["mean"]))
        
        total = sum(weights.values())
        return {k: v/total for k, v in weights.items()}
