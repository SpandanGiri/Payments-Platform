from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    payment_url: str


settings = Settings()