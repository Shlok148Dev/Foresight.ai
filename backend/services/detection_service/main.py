from fastapi import FastAPI
from kafka import KafkaConsumer, KafkaProducer
import json
import asyncio
import logging
from app.services.advanced_clustering import AdvancedClusteringEngine

app = FastAPI(title="Detection Service")
logger = logging.getLogger(__name__)

try:
    consumer = KafkaConsumer(
        'raw-signals',
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
    logger.warning("Kafka not reachable for detection_service")

clusterer = AdvancedClusteringEngine()

async def consume_and_detect():
    if not consumer: return
    signals_buffer = []
    
    for message in consumer:
        signal = message.value
        # Mock NLP Processing
        processed = {"content": signal["content"], "processed": True}
        signals_buffer.append(processed)
        
        if len(signals_buffer) >= 100:
            clusters = clusterer.cluster_signals(signals_buffer)
            for cluster_id, cluster_signals in clusters["clusters"].items():
                trend = {
                    "cluster_id": cluster_id,
                    "signals": cluster_signals,
                    "num_signals": len(cluster_signals)
                }
                if producer:
                    producer.send('detected-trends', value=trend)
            signals_buffer = []

@app.on_event("startup")
async def startup():
    asyncio.create_task(consume_and_detect())

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "detection-service"}
