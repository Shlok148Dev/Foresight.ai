from kafka import KafkaProducer, KafkaConsumer
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class EventStreamingService:
    """Kafka-based event streaming"""
    
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            self.connected = True
        except Exception as e:
            logger.warning(f"Kafka connection failed (this is expected if Kafka is not running locally): {e}")
            self.producer = None
            self.connected = False
    
    def publish_trend_event(self, trend: Dict):
        """Publish trend event"""
        if not self.connected or not self.producer:
            return
        try:
            self.producer.send('trend-events', value=trend)
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to publish trend event: {e}")
