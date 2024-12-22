#!/bin/bash
# scripts/start.sh

echo "Setting up fraud detection system..."

# Check if PostgreSQL is running
pg_isready -h localhost -p 5432
if [ $? -ne 0 ]; then
    echo "Error: PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Setup database
echo "Setting up database..."
python scripts/setup_db.py

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting the application..."
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
