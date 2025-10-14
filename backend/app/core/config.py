from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "Black-Scholes Visualization Dashboard"
    items_per_user: int = 50
    debug: bool = False
    polygon_api_key: str

settings = Settings()
