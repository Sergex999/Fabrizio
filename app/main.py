from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.carriers import get_official_url
from app.config import settings
from app.dianxiaomi_client import DianxiaomiClient
from app.email_parser import extract_customer_email, extract_order_number
from app.email_template import generate_email
from app.shopify_client import ShopifyClient, fetch_access_token
from app.yunexpress_client import YunExpressClient

app = FastAPI(title="Cor Bloom Tracking Assistant")
templates = Jinja2Templates(directory="app/templates")

_shopify_access_token_cache: Optional[str] = None


def get_shopify_client() -> Optional[ShopifyClient]:
    global _shopify_access_token_cache
    if not settings.shopify_shop_domain or not settings.shopify_client_id or not settings.shopify_client_secret:
        return None
    if not _shopify_access_token_cache:
        _shopify_access_token_cache = fetch_access_token(
            settings.shopify_shop_domain,
            settings.shopify_client_id,
            settings.shopify_client_secret,
        )
    return ShopifyClient(
        settings.shopify_shop_domain,
        _shopify_access_token_cache,
        settings.shopify_api_version,
    )


def run_pipeline(order_number: Optional[str], email: Optional[str]) -> tuple[dict, list[str]]:
    """Runs Shopify -> dianxiaomi -> YunExpress -> carrier lookup, best-effort.

    Returns the fields collected so far (blank where a step failed) and a
    list of warnings describing what needs to be filled in manually.
    """
    warnings: list[str] = []
    fields = {
        "customer_name": "",
        "carrier": "",
        "tracking_number": "",
        "tracking_url": "",
        "destination_country": "",
    }

    shopify = get_shopify_client()
    if not shopify:
        warnings.append(
            "Shopify is not configured (missing SHOPIFY_SHOP_DOMAIN / "
            "SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET in .env) — fill in all fields manually below."
        )
        return fields, warnings

    order = shopify.find_order(order_number=order_number, email=email)
    if not order:
        warnings.append(
            "No matching Shopify order was found for that order number/email. "
            "Fill in all fields manually below."
        )
        return fields, warnings

    info = shopify.extract_shipping_info(order)
    fields["customer_name"] = info["recipient_name"] or ""
    fields["destination_country"] = info["country"] or ""

    international_tracking = shopify.extract_tracking_number(order)
    if international_tracking:
        warnings.append(
            f"Using tracking number already on file in Shopify ({international_tracking}) "
            "— dianxiaomi lookup skipped."
        )
    elif fields["customer_name"]:
        dianxiaomi = DianxiaomiClient(settings.playwright_headless)
        try:
            international_tracking = dianxiaomi.find_tracking_number(fields["customer_name"])
        except Exception as exc:  # scraping is best-effort, never block the flow
            warnings.append(f"Could not look up dianxiaomi automatically ({exc}).")
        if not international_tracking:
            warnings.append(
                "Could not find a tracking number on dianxiaomi automatically — "
                "please search manually and fill in below."
            )

    if international_tracking:
        yunexpress = YunExpressClient(settings.playwright_headless)
        try:
            last_mile = yunexpress.get_last_mile(international_tracking)
        except Exception as exc:
            last_mile = None
            warnings.append(f"Could not look up YunExpress automatically ({exc}).")
        if last_mile:
            fields["carrier"] = last_mile.get("carrier") or ""
            fields["tracking_number"] = last_mile.get("local_tracking_number") or international_tracking
            fields["tracking_url"] = (
                last_mile.get("tracking_url") or get_official_url(fields["carrier"]) or ""
            )
            if not fields["tracking_url"]:
                warnings.append(
                    f"No official tracking URL known for carrier '{fields['carrier']}' — "
                    "add it to app/carriers.json or fill in below."
                )
        else:
            fields["tracking_number"] = international_tracking
            warnings.append(
                "Could not determine the Last Mile carrier on YunExpress automatically — "
                "please check yuntrack.com manually and fill in below."
            )

    return fields, warnings


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.post("/process", response_class=HTMLResponse)
def process(request: Request, raw_email: str = Form(...)):
    order_number = extract_order_number(raw_email)
    customer_email = extract_customer_email(raw_email)

    extraction_notes = []
    if order_number:
        extraction_notes.append(f"Order number found: {order_number}")
    if customer_email:
        extraction_notes.append(f"Customer email found: {customer_email}")
    if not order_number and not customer_email:
        extraction_notes.append(
            "Could not find an order number or customer email in the pasted text."
        )

    fields, warnings = run_pipeline(order_number, customer_email)

    email_text = None
    if all(fields.values()):
        email_text = generate_email(**fields)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "raw_email": raw_email,
            "extraction_notes": extraction_notes,
            "warnings": warnings,
            "email_text": email_text,
            **fields,
        },
    )


@app.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    raw_email: str = Form(""),
    customer_name: str = Form(...),
    carrier: str = Form(...),
    tracking_number: str = Form(...),
    tracking_url: str = Form(...),
    destination_country: str = Form(...),
):
    email_text = generate_email(
        customer_name=customer_name,
        carrier=carrier,
        tracking_number=tracking_number,
        tracking_url=tracking_url,
        destination_country=destination_country,
    )
    return templates.TemplateResponse(
        request,
        "index.html",
        {"raw_email": raw_email, "email_text": email_text},
    )
