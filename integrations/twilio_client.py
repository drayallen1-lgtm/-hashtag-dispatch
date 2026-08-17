"""
Twilio integration — SMS + phone number handling.

STATUS: Not yet connected. Needs a Twilio account (created by you — see
SETUP_CHECKLIST.md, step 1). Once you have an Account SID, Auth Token, and
a purchased phone number, fill in the three values below and swap
core/notifications.py's _send() function to call send_sms() from here
instead of printing.

Nothing else in the codebase needs to change — this is the only file that
touches real credentials.
"""

import os

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")


def send_sms(to_phone: str, message: str) -> dict:
    """
    Sends a real SMS via Twilio. Requires the `twilio` package
    (pip install twilio) and the three env vars above set.
    """
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER):
        raise RuntimeError(
            "Twilio credentials not configured. Set TWILIO_ACCOUNT_SID, "
            "TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables. "
            "See SETUP_CHECKLIST.md step 1."
        )

    from twilio.rest import Client  # imported lazily so the rest of the
                                     # system works without this package installed

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    result = client.messages.create(to=to_phone, from_=TWILIO_PHONE_NUMBER, body=message)
    return {"sid": result.sid, "status": result.status}
