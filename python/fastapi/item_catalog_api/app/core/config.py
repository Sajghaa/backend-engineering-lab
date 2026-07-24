from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./item_catalog.db"
    
    class Config:
        env_file = ".env" 
settings = Settings()