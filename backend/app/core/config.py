from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Local Marketplace"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "mysql+pymysql://root:Admin%401234@localhost/local_marketplace"

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    CORS_ORIGINS: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    # Email
    MAIL_FROM: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_ADMIN: str = ""

    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str

    # Return window (days after delivery within which return is allowed)
    RETURN_WINDOW_DAYS: int = 2

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()