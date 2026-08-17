"""
Intake: turns a raw call/text transcript into a structured Job.

In production, the "transcript" argument here comes from a voice AI
platform (Retell/Vapi/Bland) after it talks to the customer — that's an
external service requiring your account + API key (see
integrations/voice_agent.py and SETUP_CHECKLIST.md).

This module itself is 100% self-contained and testable right now: give it
a transcript string and it returns a Job. When you connect a real voice
agent, its output gets fed straight into parse_transcript() unchanged.
"""

import re
import uuid
from .models import Job, Customer, Trade, Urgency

TRADE_KEYWORDS = {
    Trade.PLUMBING: ["leak", "pipe", "drain", "toilet", "faucet", "water heater", "sewer", "clog"],
    Trade.HVAC: ["furnace", "ac", "air condition", "heat", "thermostat", "duct", "hvac"],
}

EMERGENCY_KEYWORDS = ["flooding", "no heat", "no ac", "gas smell", "burst pipe", "sewage", "no water"]
SAME_DAY_KEYWORDS = ["today", "asap", "as soon as possible", "urgent"]


def _detect_trade(text: str) -> Trade:
    text = text.lower()
    for trade, keywords in TRADE_KEYWORDS.items():
        if any(k in text for k in keywords):
            return trade
    return Trade.PLUMBING  # default; real system would ask a clarifying question instead


def _detect_urgency(text: str) -> Urgency:
    text = text.lower()
    if any(k in text for k in EMERGENCY_KEYWORDS):
        return Urgency.EMERGENCY
    if any(k in text for k in SAME_DAY_KEYWORDS):
        return Urgency.SAME_DAY
    return Urgency.STANDARD


def parse_transcript(transcript: str, customer_name: str, customer_phone: str, customer_address: str) -> Job:
    """
    Converts a transcript + captured contact details into a Job.
    Real deployment: the voice agent's own conversation flow should
    explicitly capture name/phone/address as structured fields rather than
    relying on parsing them out of free text — this function assumes that's
    already done and just classifies trade + urgency from the description.
    """
    job = Job(
        job_id=str(uuid.uuid4())[:8],
        customer=Customer(name=customer_name, phone=customer_phone, address=customer_address),
        trade=_detect_trade(transcript),
        description=transcript.strip(),
        urgency=_detect_urgency(transcript),
    )
    job.log("Job created from intake transcript")
    return job
