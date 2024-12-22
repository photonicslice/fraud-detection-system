import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if it exists

DATABASE_URL = os.getenv("DATABASE_URL")
