import json
from typing import Optional

from app.paths import bundle_dir

_CARRIERS_FILE = bundle_dir() / "app" / "carriers.json"


def get_official_url(carrier_name: Optional[str]) -> Optional[str]:
    if not carrier_name:
        return None
    data = json.loads(_CARRIERS_FILE.read_text())
    return data.get(carrier_name.strip().lower())
