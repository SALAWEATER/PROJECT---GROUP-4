from pydantic_settings import BaseSettings  # Changed import
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    ICD_CLIENT_ID: str = os.getenv("ICD_CLIENT_ID", "")
    ICD_CLIENT_SECRET: str = os.getenv("ICD_CLIENT_SECRET", "")
    
    class Config:
        case_sensitive = True

# Create the settings instance
settings = Settings()