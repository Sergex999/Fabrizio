import re
from typing import Optional

ORDER_NUMBER_PATTERN = re.compile(r"#?\s*(CB\d{3,8})", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def extract_order_number(text: str) -> Optional[str]:
    match = ORDER_NUMBER_PATTERN.search(text)
    return match.group(1).upper() if match else None


def extract_customer_email(text: str) -> Optional[str]:
    candidates = EMAIL_PATTERN.findall(text)
    for candidate in candidates:
        if "corbloom" not in candidate.lower():
            return candidate
    return candidates[0] if candidates else None
