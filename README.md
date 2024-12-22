# Fraud Detection System

Real-time fraud detection system built with FastAPI, SQLAlchemy, and Machine Learning.

## Features
- Real-time transaction fraud detection
- Machine learning model using XGBoost
- RESTful API using FastAPI
- PostgreSQL database with SQLAlchemy ORM
- Kafka integration for async processing

## Setup
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Setup PostgreSQL database
6. Copy `.env.example` to `.env` and update values
7. Run migrations: `alembic upgrade head`
8. Initialize ML model: `python scripts/initialize_model.py`
9. Start server: `uvicorn src.main:app --reload`

## API Documentation
Access the API documentation at: `http://localhost:8000/docs`

## Project Structure
fraud-detection-system/
├── src/
│   ├── api/
│   ├── database/
│   ├── ml/
│   ├── schemas/
│   ├── services/
│   └── config/
├── migrations/
├── scripts/
├── tests/
└── models/

## License
MIT
