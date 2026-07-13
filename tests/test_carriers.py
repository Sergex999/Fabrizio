from app.carriers import get_official_url


def test_known_carrier_case_insensitive():
    assert get_official_url("DHL") == "https://www.dhl.de"
    assert get_official_url("dhl") == "https://www.dhl.de"


def test_unknown_carrier_returns_none():
    assert get_official_url("Some Unknown Carrier") is None


def test_empty_carrier_returns_none():
    assert get_official_url("") is None
    assert get_official_url(None) is None
