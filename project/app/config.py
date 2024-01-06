import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME:    str = "TransQuality Maintenance Questionare System"
    PROJECT_VERSION: str = "1.0.0"

    DATABASE_URL:          str = os.getenv("DATABASE_URL")
    MONGO_INITDB_DATABASE: str = os.getenv("MONGO_INITDB_DATABASE")

    JWT_ALGORITHM:   str = os.getenv("JWT_ALGORITHM")
    JWT_PUBLIC_KEY:  str = os.getenv("JWT_PUBLIC_KEY")
    JWT_PRIVATE_KEY: str = os.getenv("JWT_PRIVATE_KEY")

    REFRESH_TOKEN_EXPIRES_IN: int = os.getenv("REFRESH_TOKEN_EXPIRES_IN")
    ACCESS_TOKEN_EXPIRES_IN:  int = os.getenv("ACCESS_TOKEN_EXPIRES_IN")

    CLIENT_ORIGIN: str = os.getenv("CLIENT_ORIGIN")


    class Config:
        env_file = './.env'


settings = Settings()