from app.email_template import generate_email


def test_generate_email_fills_all_fields():
    text = generate_email(
        customer_name="Maria Rossi",
        carrier="DHL",
        tracking_number="1234567890",
        tracking_url="https://www.dhl.de",
        destination_country="Italy",
    )
    assert "Dear Maria Rossi," in text
    assert "* Carrier: DHL" in text
    assert "* Tracking Number: 1234567890" in text
    assert "* Tracking Website: https://www.dhl.de" in text
    assert "Italy" in text
    assert "the DHL link above" in text
    assert "Estimated Delivery" not in text
    assert text.strip().endswith("Cor Bloom Jewelry Customer Care Team \U0001F48E")
