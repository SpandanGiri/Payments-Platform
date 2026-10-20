from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    ledger_url: str

settings = Settings()