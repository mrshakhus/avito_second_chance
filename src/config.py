from typing import Literal
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVER_ADDRESS: str
    POSTGRES_CONN: str

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE: str

    model_config = ConfigDict(env_file=".env")

settings = Settings()
