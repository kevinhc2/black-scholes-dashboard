from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "Black-Scholes Dashboard"
    items_per_user: int = 50
    debug: bool = False
    polygon_api_key: str

settings = Settings()
