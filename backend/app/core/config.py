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
    # Feature flag: when False the OAuth flow is disabled and the app will use
    # an email OTP signup flow instead. Set to True to enable Entra/OAuth.
    ENABLE_OAUTH: bool = False

    # Optional SMTP settings for sending OTP emails. If not provided the
    # OTP will be logged instead of being sent.
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None
    SMTP_FROM: str | None = None

    # OTP settings
    OTP_EXPIRY_MINUTES: int = 10

    ## sessions ##
    SESSION_SECRET: str = "change-me"
    
    ## database ##
    DATABASE_URL: str = "sqlite:///./aub_reviews.db"  # Default to SQLite for local dev

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

