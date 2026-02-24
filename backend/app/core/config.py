from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ## app ##
    APP_NAME: str = "AfterClass"
    ENV: str = "dev"

    ## auth — Microsoft Entra ID ##
    ENTRA_TENANT_ID: str | None = None
    ENTRA_CLIENT_ID: str | None = None
    ENTRA_CLIENT_SECRET: str | None = None
    ENTRA_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    ENTRA_AUTHORITY: str | None = None
    ENABLE_OAUTH: bool = False

    ## frontend ##
    FRONTEND_URL: str = "http://localhost:5173"

    ## email / OTP ##
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None
    SMTP_FROM: str | None = None
    OTP_EXPIRY_MINUTES: int = 10

    ## encryption ##
    FIELD_ENCRYPTION_KEY: str = ""  # base64-encoded 32 bytes — required in prod
    FIELD_HMAC_KEY: str = ""        # long random string — required in prod

    ## sessions ##
    SESSION_SECRET: str = "change-me"

    ## database ##
    DATABASE_URL: str = "sqlite:///./aub_reviews.db"

    ## jwt ##
    JWT_SECRET: str = "change-me-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()