import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    openai_api_key: str = ""
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
    
    @property
    def allowed_origins(self) -> List[str]:
        return [self.frontend_url, "http://localhost:3000", "http://localhost:8000"]

settings = Settings()