import os

from dotenv import load_dotenv

from app.paths import app_dir

load_dotenv(app_dir() / ".env")


class Settings:
    shopify_shop_domain: str = os.environ.get("SHOPIFY_SHOP_DOMAIN", "")
    shopify_client_id: str = os.environ.get("SHOPIFY_CLIENT_ID", "")
    shopify_client_secret: str = os.environ.get("SHOPIFY_CLIENT_SECRET", "")
    shopify_api_version: str = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

    playwright_headless: bool = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() != "false"


settings = Settings()
