"""
Core data models for Hashtag Dispatch.

These are deliberately simple, dependency-free classes so the logic in
scheduling.py / escalation.py / intake.py can be tested and demonstrated
without any external services (Twilio, a voice AI platform, a real
database) being connected yet. Once those are wired up, real data will
flow into these same shapes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Trade(str, Enum):
    PLUMBING = "plumbing"
    HVAC = "hvac"


class Urgency(str, Enum):
    EMERGENCY = "emergency"      # no heat/AC in extreme weather, active leak/flood, gas smell
    SAME_DAY = "same_day"        # wants it fixed today, not an emergency
    STANDARD = "standard"        # flexible, within the week


class JobStatus(str, Enum):
    NEW = "new"
    SCHEDULED = "scheduled"
    ASSIGNED = "assigned"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"
    ESCALATED = "escalated"      # needs a human before it can move forward


@dataclass
class Customer:
    name: str
    phone: str
    address: str


@dataclass
class Technician:
    tech_id: str
    name: str
    phone: str
    trades: list[Trade]
    home_base: str                       # address/zip used for distance estimates
    available_windows: list[tuple]       # list of (datetime_start, datetime_end)
    active: bool = True


@dataclass
class Job:
    job_id: str
    customer: Customer
    trade: Trade
    description: str
    urgency: Urgency
    status: JobStatus = JobStatus.NEW
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_window: Optional[tuple] = None
    assigned_tech: Optional[Technician] = None
    escalation_reason: Optional[str] = None
    notes: list[str] = field(default_factory=list)

    def log(self, message: str):
        self.notes.append(f"[{datetime.now().isoformat(timespec='seconds')}] {message}")


@dataclass
class Business:
    business_id: str
    name: str
    trades: list[Trade]
    service_area: str
    technicians: list[Technician]
    business_hours: tuple = (("07:00", "18:00"),)
    emergency_service: bool = True
