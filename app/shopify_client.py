from typing import Optional

import requests


def fetch_access_token(shop_domain: str, client_id: str, client_secret: str) -> str:
    """Obtains an Admin API access token via the client credentials grant.

    This is how custom apps built through the Shopify Dev Dashboard get an
    access token for a single store, without a static "reveal token" button
    in the admin UI.
    """
    resp = requests.post(
        f"https://{shop_domain}/admin/oauth/access_token",
        json={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


class ShopifyClient:
    """Looks up orders in Shopify Admin API by order number or customer email."""

    def __init__(self, shop_domain: str, access_token: str, api_version: str = "2024-01"):
        self.base_url = f"https://{shop_domain}/admin/api/{api_version}"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }

    def find_order(self, order_number: Optional[str] = None, email: Optional[str] = None) -> Optional[dict]:
        if order_number:
            order = self._find_by_order_number(order_number)
            if order:
                return order
        if email:
            return self._find_latest_by_email(email)
        return None

    def _find_by_order_number(self, order_number: str) -> Optional[dict]:
        name = order_number if order_number.startswith("#") else f"#{order_number}"
        resp = requests.get(
            f"{self.base_url}/orders.json",
            headers=self.headers,
            params={"name": name, "status": "any"},
            timeout=15,
        )
        resp.raise_for_status()
        orders = resp.json().get("orders", [])
        return orders[0] if orders else None

    def _find_latest_by_email(self, email: str) -> Optional[dict]:
        resp = requests.get(
            f"{self.base_url}/orders.json",
            headers=self.headers,
            params={
                "email": email,
                "status": "any",
                "limit": 1,
                "order": "created_at desc",
            },
            timeout=15,
        )
        resp.raise_for_status()
        orders = resp.json().get("orders", [])
        return orders[0] if orders else None

    @staticmethod
    def extract_shipping_info(order: dict) -> dict:
        shipping = order.get("shipping_address") or {}
        return {
            "order_number": order.get("name"),
            "recipient_name": shipping.get("name"),
            "country": shipping.get("country"),
            "email": order.get("email"),
        }

    @staticmethod
    def extract_tracking_number(order: dict) -> Optional[str]:
        """Returns the tracking number Shopify already has on file, if the
        order has been fulfilled. Freight forwarders like dianxiaomi write
        this back to Shopify when they generate a shipping label."""
        for fulfillment in order.get("fulfillments") or []:
            tracking_number = fulfillment.get("tracking_number")
            if tracking_number:
                return tracking_number
        return None
