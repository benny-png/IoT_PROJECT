from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    AT_USERNAME: str
    AT_API_KEY: str
    OPENAI_API_KEY: str
    # Define it as a list with a default value
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Use model_config instead of Config in newer Pydantic versions
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

settings = Settings()