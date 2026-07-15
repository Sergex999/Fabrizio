from app.email_template import generate_email, generate_preheader, generate_subject


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


def test_generate_subject():
    subject = generate_subject()
    assert subject == "Your Cor Bloom order is on its way \U0001F48E Tracking info inside"
    assert "\n" not in subject


def test_generate_preheader_fills_all_fields():
    preheader = generate_preheader(
        carrier="DHL",
        tracking_number="1234567890",
        destination_country="Italy",
    )
    assert "Italy" in preheader
    assert "DHL" in preheader
    assert "1234567890" in preheader
    assert "\n" not in preheader
