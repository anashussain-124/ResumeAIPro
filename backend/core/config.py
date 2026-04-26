from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field
from typing import Optional

class Settings(BaseSettings):
    mongodb_uri: str = Field(default="mongodb://localhost:27017")
    openai_api_key: str = Field(default="")
    razorpay_key_id: str = Field(default="")
    razorpay_key_secret: str = Field(default="")
    frontend_url: str = Field(default="http://localhost:3000")
    secret_key: str = Field(default="supersecretkey-change-in-production")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
