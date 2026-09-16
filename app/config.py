import os
from dotenv import load_dotenv

# Load environment variables from the project root or the data directory.
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", ".env"))

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    CHROMA_PERSIST_DIR: str = "./storage"
    DATA_DIR: str = "./data"

settings = Settings()

# Ensure directories exist upon initialization
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)