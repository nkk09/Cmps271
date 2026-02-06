from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ## app ##
    APP_NAME: str = "AUB Reviews"
    ENV: str = "dev"
    ## auth ##
    ENTRA_TENANT_ID: str | None = None
    ENTRA_CLIENT_ID: str | None = None
    ENTRA_CLIENT_SECRET: str | None = None
    ENTRA_REDIRECT_URI: str | None = None
    ENTRA_AUTHORITY: str | None = None

    ## sessions ##
    SESSION_SECRET: str = "change-me"
    
    ## database ##
    DATABASE_URL: str = "sqlite:///./aub_reviews.db"  # Default to SQLite for local dev

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

