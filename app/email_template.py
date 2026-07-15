TEMPLATE = """Dear {customer_name},

Here is your tracking information:

* Carrier: {carrier}
* Tracking Number: {tracking_number}
* Tracking Website: {tracking_url}

Your package is currently in transit on an international flight to {destination_country}. You can continue to track it using the {carrier} link above with your tracking number.

Once the shipment arrives and clears customs, it will be handed over to your local postal service for final delivery. At that point, more detailed tracking updates will begin to appear – so if you don't see an update just yet, please rest assured that your package is moving as quickly as possible.

Thank you so much for your patience, understanding, and support. We are truly grateful and look forward to delivering your order very soon!

If you have any questions, feel free to reply – I'm here to help.

Kind regards,
Amanda
Cor Bloom Jewelry Customer Care Team \U0001F48E
"""


SUBJECT_TEMPLATE = "Your Cor Bloom order is on its way \U0001F48E Tracking info inside"

PREHEADER_TEMPLATE = (
    "Your package is traveling to {destination_country} — track it with "
    "{carrier} using tracking number {tracking_number}."
)


def generate_subject() -> str:
    return SUBJECT_TEMPLATE


def generate_preheader(
    carrier: str,
    tracking_number: str,
    destination_country: str,
) -> str:
    return PREHEADER_TEMPLATE.format(
        carrier=carrier,
        tracking_number=tracking_number,
        destination_country=destination_country,
    )


def generate_email(
    customer_name: str,
    carrier: str,
    tracking_number: str,
    tracking_url: str,
    destination_country: str,
) -> str:
    return TEMPLATE.format(
        customer_name=customer_name,
        carrier=carrier,
        tracking_number=tracking_number,
        tracking_url=tracking_url,
        destination_country=destination_country,
    )
