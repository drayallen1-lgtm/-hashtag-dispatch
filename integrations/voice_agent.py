"""
Voice AI agent integration — the system that actually answers the phone.

STATUS: Not yet connected. This requires picking ONE platform (see
SETUP_CHECKLIST.md step 2 for a comparison) and creating an account there:

  - Retell AI   (retellai.com)
  - Vapi        (vapi.ai)
  - Bland AI    (bland.ai)

All three work roughly the same way: you configure a phone number, give
the platform a system prompt / call script (see CALL_SCRIPT.md — built
separately once you're ready for it), and they send call transcripts to a
webhook URL you provide as each call happens.

This file is where that webhook handler will live. Right now it's a
skeleton showing the shape: once a call finishes, the platform POSTs a
transcript here, this function hands it to core/intake.py, and the normal
pipeline takes over from there — no code changes needed anywhere else.
"""

from core.intake import parse_transcript
from core.dispatcher import handle_job


def handle_call_webhook(payload: dict, business, owner_phone: str):
    """
    payload shape will depend on which platform you pick — this assumes a
    generic shape with transcript + captured customer fields, which is
    close to what all three platforms provide. Adjust field names once a
    platform is chosen and its real webhook payload is visible.
    """
    transcript = payload.get("transcript", "")
    customer_name = payload.get("customer_name", "")
    customer_phone = payload.get("customer_phone", "")
    customer_address = payload.get("customer_address", "")

    job = parse_transcript(transcript, customer_name, customer_phone, customer_address)
    return handle_job(job, business, owner_phone)
