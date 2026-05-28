from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncio
from kafka import KafkaProducer
import json
import logging

app = FastAPI(title="Signal Service")
logger = logging.getLogger(__name__)

class Signal(BaseModel):
    platform: str
    content: str
    author: str
    timestamp: str
    url: str

try:
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except Exception as e:
    producer = None
    logger.warning("Kafka not reachable for signal_service")

@app.post("/signals/ingest")
async def ingest_signal(signal: Signal):
    """Ingest single signal"""
    if not signal.content:
        raise HTTPException(status_code=400, detail="Content required")
    
    signal_dict = signal.dict()
    # In a real app we'd save to DB here
    # db_signal = db.create_signal(signal_dict)
    
    if producer:
        producer.send('raw-signals', value=signal_dict)
    
    return {"signal_id": "mock_id", "status": "ingested"}

@app.post("/signals/batch")
async def ingest_batch(signals: List[Signal]):
    """Ingest multiple signals"""
    results = []
    for signal in signals:
        try:
            result = await ingest_signal(signal)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    return results

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "signal-service"}
