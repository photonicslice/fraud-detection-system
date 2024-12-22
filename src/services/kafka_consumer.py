from kafka import KafkaConsumer
import json
from src.ml.model import FraudDetectionModel
from src.database.connection import SessionLocal
from src.services.transaction_service import TransactionService

class TransactionConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'transactions',
            bootstrap_servers=['localhost:9092'],
            group_id='fraud_detection_group',
            auto_offset_reset='latest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.model = FraudDetectionModel()
        self.model.load_model()

    async def start_consuming(self):
        try:
            for message in self.consumer:
                await self.process_transaction(message.value)
        finally:
            self.consumer.close()

    async def process_transaction(self, transaction_data):
        db = SessionLocal()
        try:
            transaction_service = TransactionService(db)
            enriched_data = transaction_service.enrich_transaction(transaction_data)
            fraud_probability = self.model.predict(enriched_data)
            transaction_service.store_transaction(transaction_data, fraud_probability)
        finally:
            db.close()
