from fastapi import FastAPI
from kafka import KafkaConsumer, KafkaProducer
import json
import asyncio
import logging
from app.services.forecasting_ensemble import EnsembleForecaster

app = FastAPI(title="Forecast Service")
logger = logging.getLogger(__name__)

try:
    consumer = KafkaConsumer(
        'detected-trends',
        bootstrap_servers=['kafka:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except Exception:
    consumer = None
    producer = None
    logger.warning("Kafka not reachable for forecast_service")

forecaster = EnsembleForecaster()

async def consume_and_forecast():
    if not consumer: return
    for message in consumer:
        trend = message.value
        # Mock DB history call
        history = [{"count": 100}]
        forecast = forecaster.forecast_trend(history, periods=21)
        if producer:
            producer.send('trend-forecasts', value={
                "trend_id": trend["cluster_id"],
                "forecast": forecast
            })

@app.on_event("startup")
async def startup():
    asyncio.create_task(consume_and_forecast())

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "forecast-service"}
