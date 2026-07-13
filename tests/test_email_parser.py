from app.email_parser import extract_customer_email, extract_order_number


def test_extract_order_number_with_hash():
    assert extract_order_number("Hi, my order is #CB56526 and it's late") == "CB56526"


def test_extract_order_number_without_hash():
    assert extract_order_number("order CB1234 status?") == "CB1234"


def test_extract_order_number_missing():
    assert extract_order_number("Where is my package?") is None


def test_extract_customer_email_prefers_non_corbloom_address():
    text = "From: jane.doe@example.com\nTo: amanda@corbloomjewelry.com\n\nWhere is my order?"
    assert extract_customer_email(text) == "jane.doe@example.com"


def test_extract_customer_email_missing():
    assert extract_customer_email("no email here") is None
