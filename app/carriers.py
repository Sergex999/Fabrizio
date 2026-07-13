import json
from pathlib import Path
from typing import Optional

_CARRIERS_FILE = Path(__file__).parent / "carriers.json"


def get_official_url(carrier_name: Optional[str]) -> Optional[str]:
    if not carrier_name:
        return None
    data = json.loads(_CARRIERS_FILE.read_text())
    return data.get(carrier_name.strip().lower())
