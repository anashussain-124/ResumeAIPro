from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb+srv://anashussain7075020_admin:PAssword123@cluster0.6zojzfx.mongodb.net/?appName=Cluster0"
    openai_api_key: str = ""
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()