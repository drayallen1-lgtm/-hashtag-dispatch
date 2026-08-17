"""
Notifications: confirmations to customers, job alerts to techs.

send_sms() is the one function that needs a real Twilio account connected
(see integrations/twilio_client.py + SETUP_CHECKLIST.md). Until that's
wired up, it just logs what WOULD be sent, so the rest of the system is
fully testable without any external accounts.
"""

from .models import Job, Technician


def _send(to_phone: str, message: str) -> None:
    # Placeholder — swap this body for integrations.twilio_client.send_sms()
    # once a Twilio account + phone number exist.
    print(f"[SMS -> {to_phone}] {message}")


def notify_customer_confirmation(job: Job) -> None:
    window = job.scheduled_window
    when = f"{window[0].strftime('%a %b %d, %I:%M %p')}" if window else "TBD"
    msg = (
        f"Hi {job.customer.name}, you're booked for {job.trade.value} service "
        f"on {when}. We'll text you when your technician is on the way. "
        f"Reply STOP to opt out."
    )
    _send(job.customer.phone, msg)
    job.log("Customer confirmation sent")


def notify_technician_assignment(job: Job) -> None:
    if not job.assigned_tech:
        return
    msg = (
        f"New job: {job.trade.value} at {job.customer.address}. "
        f"Customer: {job.customer.name} ({job.customer.phone}). "
        f"Issue: {job.description}. Job ID {job.job_id}."
    )
    _send(job.assigned_tech.phone, msg)
    job.log(f"Technician {job.assigned_tech.name} notified")


def notify_human_escalation(job: Job, owner_phone: str) -> None:
    msg = (
        f"[ESCALATION] Job {job.job_id} needs your review: {job.escalation_reason}. "
        f"Customer: {job.customer.name} ({job.customer.phone})."
    )
    _send(owner_phone, msg)
    job.log("Escalation alert sent to human")
