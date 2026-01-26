import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Static files
    static_dir: str = os.path.join(os.path.dirname(__file__), "..", "ui", "dist")

    class Config:
        env_prefix = "MINERU_CENTER_"


settings = Settings()
