from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "Nexus d20"
    app_env: str = "development"
    app_url: str = "http://localhost:3000"
    database_url: str = "postgresql+asyncpg://nexus:nexus@localhost:5432/nexus_d20"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = Field(default="development-only-secret-change-me")
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    password_reset_ttl_minutes: int = 30
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = False
    mail_from: str = "nao-responda@nexus-d20.local"
    s3_endpoint: str = "http://localhost:9000"
    s3_public_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "nexus-d20"
    s3_access_key: str = "nexus_minio"
    s3_secret_key: str = "nexus_minio_change_me"
    s3_region: str = "us-east-1"
    media_max_bytes: int = 10 * 1024 * 1024
    rate_limit_enabled: bool = False
    rate_limit_requests_per_minute: int = 120
    auth_rate_limit_requests_per_minute: int = 10
    trust_proxy_headers: bool = False
    metrics_token: str = ""
    audit_retention_days: int = 730
    session_retention_days: int = 90
    cors_origins_raw: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def secure_cookies(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
