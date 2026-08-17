"""
The orchestrator: wires intake -> escalation check -> scheduling ->
assignment -> notifications into one pipeline. This is "Hashtag Dispatch"
end to end, running with zero human involvement unless escalation.needs_escalation()
says otherwise.
"""

from .models import Business, Job, JobStatus
from .escalation import needs_escalation
from .scheduling import find_technician, propose_windows
from .notifications import notify_customer_confirmation, notify_technician_assignment, notify_human_escalation


def handle_job(job: Job, business: Business, owner_phone: str) -> Job:
    escalate, reason = needs_escalation(job)
    if escalate:
        job.status = JobStatus.ESCALATED
        job.escalation_reason = reason
        notify_human_escalation(job, owner_phone)
        return job

    windows = propose_windows(job.urgency)
    chosen_window = windows[0]  # real system: customer picks via voice/text menu

    tech = find_technician(job, business.technicians, chosen_window)
    if tech is None:
        job.status = JobStatus.ESCALATED
        job.escalation_reason = "No available technician found for this trade/window"
        notify_human_escalation(job, owner_phone)
        return job

    job.scheduled_window = chosen_window
    job.assigned_tech = tech
    job.status = JobStatus.CONFIRMED
    job.log(f"Auto-scheduled with {tech.name} for {chosen_window[0]}")

    notify_technician_assignment(job)
    notify_customer_confirmation(job)
    return job
