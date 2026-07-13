import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    shopify_shop_domain: str = os.environ.get("SHOPIFY_SHOP_DOMAIN", "")
    shopify_client_id: str = os.environ.get("SHOPIFY_CLIENT_ID", "")
    shopify_client_secret: str = os.environ.get("SHOPIFY_CLIENT_SECRET", "")
    shopify_api_version: str = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

    dianxiaomi_username: str = os.environ.get("DIANXIAOMI_USERNAME", "")
    dianxiaomi_password: str = os.environ.get("DIANXIAOMI_PASSWORD", "")

    playwright_headless: bool = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() != "false"


settings = Settings()
