"""
Configuration module for AI API Gateway
Uses environment variables for configuration
"""
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from functools import lru_cache

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    """Application settings"""
    
    # Azure OpenAI settings
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_MODEL: str = os.getenv("AZURE_OPENAI_MODEL", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "")

    # Default system prompt
    DEFAULT_SYSTEM_PROMPT: str = os.getenv("DEFAULT_SYSTEM_PROMPT", "You are a helpful AI assistant.")

    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]

    # AI Provider settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "azure")
    DIGITALOCEAN_INFERENCE_ENDPOINT: str = os.getenv("DIGITALOCEAN_INFERENCE_ENDPOINT", "")
    DIGITALOCEAN_API_KEY: str = os.getenv("DIGITALOCEAN_API_KEY", "")
    DIGITALOCEAN_MODEL: str = os.getenv("DIGITALOCEAN_MODEL", "")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
