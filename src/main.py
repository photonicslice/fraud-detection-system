from fastapi import FastAPI
from src.api.routes import router as api_router
from src.database.connection import engine
from src.database.models import Base

app = FastAPI(title="Fraud Detection System")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
