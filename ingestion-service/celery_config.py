import os
from celery import Celery
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://redis:6379"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/classgpt"

    class Config:
        env_file = ".env"

settings = Settings()

# Create Celery app
celery_app = Celery(
    "ingestion_service",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
) 