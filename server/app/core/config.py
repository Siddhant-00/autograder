# app/core/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_PATH: str = "uploads/"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")  # Make sure this points to your .env file
        extra = "ignore" 

settings = Settings()
