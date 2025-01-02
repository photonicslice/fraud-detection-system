from fastapi import FastAPI
from src.api.routes import router as api_router
from src.database.connection import engine
from src.database.models import Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fraud Detection System")

# Create database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


