from prometheus_client import Counter, Histogram, Gauge
import time
from fastapi import Request

# Metrics
signals_ingested = Counter('signals_ingested_total', 'Total signals ingested')
trends_detected = Counter('trends_detected_total', 'Total trends detected')
forecasts_generated = Counter('forecasts_generated_total', 'Total forecasts generated')

signal_processing_time = Histogram('signal_processing_seconds', 'Signal processing time')
forecast_latency = Histogram('forecast_latency_seconds', 'Forecast generation latency')

active_trends = Gauge('active_trends', 'Number of active trends')
kafka_lag = Gauge('kafka_lag', 'Kafka consumer lag')

async def add_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    # Record metrics
    if request.url.path == "/signals/ingest":
        signals_ingested.inc()
        signal_processing_time.observe(duration)
    
    return response
