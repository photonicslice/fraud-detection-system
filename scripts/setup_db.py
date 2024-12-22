# scripts/setup_db.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os

def setup_database():
    load_dotenv()

    # Database connection parameters
    dbname = "fraud_detection"
    user = "fraud_user"
    password = "fraud7"
    host = "localhost"
    
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host=host
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Create database if it doesn't exist
    try:
        cur.execute(f"CREATE DATABASE {dbname}")
        print(f"Database {dbname} created successfully")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database {dbname} already exists")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cur.close()
        conn.close()

    # Create user if doesn't exist
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host
    )
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE USER {user} WITH PASSWORD '{password}'")
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {user}")
        print(f"User {user} created successfully")
    except psycopg2.errors.DuplicateObject:
        print(f"User {user} already exists")
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_database()
