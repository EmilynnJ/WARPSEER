from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, Field
from typing import Optional
import json

class Settings(BaseSettings):
    app_name: str = Field(default="SoulSeer")
    admin_email: str

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    clerk_secret_key: str
    clerk_jwks_url: Optional[AnyHttpUrl] = None
    clerk_issuer: Optional[str] = None

    stripe_secret_key: str
    stripe_webhook_signing_secret: str

    frontend_public_url: Optional[str] = None
    backend_public_url: Optional[str] = None

    reader_share_pct: int = 70  # percent to readers

    webrtc_turn_servers: str = "relay1.expressturn.com:3480"
    webrtc_turn_username: Optional[str] = None
    webrtc_turn_credential: Optional[str] = None
    webrtc_ice_servers: str = '[{"urls":"stun:stun.l.google.com:19302"},{"urls":"stun:stun1.l.google.com:19302"}]'

    s3_endpoint: Optional[str] = None
    s3_region: Optional[str] = None
    s3_bucket: Optional[str] = None
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None

    sentry_dsn_backend: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ice_servers(self):
        try:
            return json.loads(self.webrtc_ice_servers)
        except Exception:
            return []

settings = Settings()  # type: ignore