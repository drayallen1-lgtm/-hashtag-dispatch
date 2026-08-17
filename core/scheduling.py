"""
Scheduling and technician assignment.

find_technician() picks the best available tech for a job. The distance
calculation here is a placeholder (string comparison) — in the real system
this gets replaced with an actual geocoding + drive-time API call (e.g.
Google Maps Distance Matrix), which is one of the setup steps that needs
an API key from you.
"""

from datetime import datetime
from .models import Job, Technician, Urgency


def _is_available(tech: Technician, window: tuple) -> bool:
    if not tech.active:
        return False
    start, end = window
    for avail_start, avail_end in tech.available_windows:
        if avail_start <= start and end <= avail_end:
            return True
    return False


def _distance_score(tech: Technician, job_address: str) -> int:
    """
    Placeholder scoring: real version calls a maps API for drive time.
    For now, technicians whose home_base shares a city/town name with the
    job address score better — good enough for pilot-stage demos, not for
    production.
    """
    tech_area = tech.home_base.split(",")[0].strip().lower()
    job_area = job_address.split(",")[0].strip().lower()
    return 0 if tech_area == job_area else 1


def find_technician(job: Job, technicians: list[Technician], window: tuple) -> Technician | None:
    """
    Returns the best matching technician for a job + time window, or None
    if nobody qualifies (wrong trade, nobody available) — which should
    trigger escalation upstream.
    """
    candidates = [
        t for t in technicians
        if job.trade in t.trades and _is_available(t, window)
    ]
    if not candidates:
        return None

    candidates.sort(key=lambda t: _distance_score(t, job.customer.address))
    return candidates[0]


def propose_windows(urgency: Urgency, now: datetime | None = None) -> list[tuple]:
    """
    Suggests candidate scheduling windows based on urgency. Emergency jobs
    get "as soon as possible" windows; standard jobs get more relaxed
    same-week windows. This is what the AI intake agent would offer the
    customer to pick from.
    """
    now = now or datetime.now()
    if urgency == Urgency.EMERGENCY:
        return [(now, now.replace(hour=min(now.hour + 2, 23)))]
    if urgency == Urgency.SAME_DAY:
        return [(now.replace(hour=13, minute=0), now.replace(hour=17, minute=0))]
    # standard: offer next two business days, morning/afternoon
    return [
        (now.replace(hour=9, minute=0), now.replace(hour=12, minute=0)),
        (now.replace(hour=13, minute=0), now.replace(hour=17, minute=0)),
    ]
