from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.ml.model import FraudDetectionModel
from src.schemas.transaction import TransactionCreate, TransactionResponse
from src.services.transaction_service import TransactionService

router = APIRouter()
model = FraudDetectionModel()
model.load_model()

@router.post("/transactions/verify", response_model=TransactionResponse)
async def verify_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    transaction_service = TransactionService(db)
    
    # Process transaction
    try:
        # Enrich transaction data
        enriched_data = transaction_service.enrich_transaction(transaction)
        
        # Get fraud prediction
        fraud_probability = model.predict(enriched_data)
        
        # Store result
        result = transaction_service.store_transaction(
            transaction, 
            fraud_probability
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
