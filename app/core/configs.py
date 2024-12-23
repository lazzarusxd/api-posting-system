from os import environ

from pydantic import BaseModel


class Settings(BaseModel):

    API_V1: str = "/api/v1"
    DB_URL: str = environ.get("DB_URL")
    JWT_SECRET: str = environ.get("JWT_SECRET")
    ALGORITHM: str = environ.get("ALGORITHM")
    TOKEN_EXPIRATION_MINUTES: int = int(environ.get("TOKEN_EXPIRATION_MINUTES"))
    RABBITMQ_HOST: str = environ.get("RABBITMQ_HOST")
    RABBITMQ_PORT: int = int(environ.get("RABBITMQ_PORT"))
    RABBITMQ_DEFAULT_USER: str = environ.get("RABBITMQ_DEFAULT_USER")
    RABBITMQ_DEFAULT_PASS: str = environ.get("RABBITMQ_DEFAULT_PASS")
    REDIS_HOST: str = environ.get("REDIS_HOST")
    REDIS_PORT: int = int(environ.get("REDIS_PORT"))
    REDIS_PASSWORD: str = environ.get("REDIS_PASSWORD")

    class Config:
        case_sensitive = True


settings: Settings = Settings()
