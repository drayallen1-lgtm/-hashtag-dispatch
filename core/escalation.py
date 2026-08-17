"""
Escalation logic: the single most important file in this system.

This is what makes "fully automated" safe rather than reckless. The system
should handle everything routine on its own, and hand off to a human ONLY
for the cases below. Tune this list as you run real pilots — you will
discover new escalation triggers from real calls that aren't listed here
yet, and this file is where you add them.
"""

from .models import Job, Urgency, Trade

# Keywords that, if mentioned during intake, should always escalate
# regardless of anything else. Err on the side of adding to this list —
# a false-positive escalation costs a human two minutes; a missed one
# could cost someone's safety or the business a lawsuit.
HARD_ESCALATION_KEYWORDS = [
    "gas smell", "gas leak", "smell gas",
    "carbon monoxide", "co detector",
    "sparking", "smoke", "fire",
    "flooding", "water everywhere", "ceiling collapsed",
    "injury", "hurt", "burned",
    "lawsuit", "lawyer", "sue",
    "refund", "complaint", "angry", "unacceptable",
]


def needs_escalation(job: Job) -> tuple[bool, str | None]:
    """
    Returns (True, reason) if this job should be routed to a human instead
    of handled automatically. Returns (False, None) if it's safe for the
    automated system to keep handling end-to-end.
    """
    text = job.description.lower()

    for keyword in HARD_ESCALATION_KEYWORDS:
        if keyword in text:
            return True, f"Safety/sensitive keyword detected: '{keyword}'"

    if job.urgency == Urgency.EMERGENCY:
        return True, "Marked emergency — confirm before auto-dispatching (until pilot proves the pattern)"

    if job.customer.address.strip() == "":
        return True, "No service address captured — can't route without one"

    return False, None


def is_vip_or_repeat_complaint(customer_phone: str, complaint_history: dict) -> bool:
    """
    Placeholder for later: once you have real customer history, flag repeat
    complainers or VIP accounts for human handling rather than the standard
    automated flow. complaint_history would come from the CRM integration.
    """
    return complaint_history.get(customer_phone, 0) >= 2
