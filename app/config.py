import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "VeriScribe — Academic Intelligence Engine"
    APP_PORT: int = 8000
    APP_HOST: str = "127.0.0.1"

    # Upload Limits
    MAX_UPLOAD_SIZE_MB: int = 50

    # Model Configuration
    MODEL_NAME: str = "sshleifer/distilbart-cnn-12-6"

    # Chunking Configuration
    CHUNK_SIZE_TOKENS: int = 800
    CHUNK_OVERLAP_TOKENS: int = 100

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

SUMMARIZATION_MODES = {
    "abstract": {"min_length": 100, "max_length": 250},
    "brief": {"min_length": 30, "max_length": 80},
    "key_points": {"min_length": 80, "max_length": 200},
    "detailed": {"min_length": 200, "max_length": 400},
    "authentic": {"min_length": 50, "max_length": 500},
}
