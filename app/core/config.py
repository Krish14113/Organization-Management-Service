from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MASTER_DB: str = "master_db"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
