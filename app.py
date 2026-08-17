"""
app.py — the live web service that Retell's webhook talks to.

This is the ONE piece that needs to run on a real hosting service (not
just on a local machine) because it needs a public internet address for
Retell to send call data to.

What it does, end to end, with zero human involvement:
  1. Retell finishes a call, POSTs the extracted data to /webhook
  2. This receives it, builds a Job from it (core/intake.py-compatible shape)
  3. Runs it through the full pipeline (core/dispatcher.py) —
     escalation check, scheduling, technician assignment, notifications
  4. Returns 200 OK to Retell

Run locally to test:
    pip install flask --break-system-packages
    python3 app.py
    (then use a tool like curl or Postman to POST test data to
    http://localhost:8080/webhook)

Deployed (e.g. on Render), this same file runs continuously and receives
real calls.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import os

from core.models import Business, Technician, Trade, Customer, Job, Urgency
from core.dispatcher import handle_job

app = Flask(__name__)

# ---------------------------------------------------------------------------
# BUSINESS CONFIG — replace with real data once you have a real pilot business.
# For now this matches the demo.py setup (Southeast Kansas Plumbing & Air).
# ---------------------------------------------------------------------------
OWNER_PHONE = os.environ.get("OWNER_PHONE", "+16205550100")

now_window = (datetime.now().replace(hour=6), datetime.now().replace(hour=22))

TECHNICIANS = [
    Technician(tech_id="T1", name="Mike R.", phone="+16205550111",
               trades=[Trade.PLUMBING], home_base="Chanute, KS",
               available_windows=[now_window]),
    Technician(tech_id="T2", name="Dana K.", phone="+16205550122",
               trades=[Trade.HVAC], home_base="Independence, KS",
               available_windows=[now_window]),
    Technician(tech_id="T3", name="Alex P.", phone="+16205550133",
               trades=[Trade.PLUMBING, Trade.HVAC], home_base="Parsons, KS",
               available_windows=[now_window]),
]

BUSINESS = Business(
    business_id="B1",
    name="Test Plumbing Co.",
    trades=[Trade.PLUMBING, Trade.HVAC],
    service_area="Southeast Kansas",
    technicians=TECHNICIANS,
)


def _urgency_from_payload(data: dict) -> Urgency:
    """Retell's extracted fields include is_urgent + timeline; map those to
    the Urgency enum core/scheduling.py expects."""
    if str(data.get("is_urgent", "")).lower() == "true":
        return Urgency.EMERGENCY
    timeline = (data.get("timeline") or "").lower()
    if "today" in timeline or "asap" in timeline or "urgent" in timeline:
        return Urgency.SAME_DAY
    return Urgency.STANDARD


@app.route("/webhook", methods=["POST"])
def retell_webhook():
    payload = request.get_json(force=True, silent=True) or {}

    call_data = payload.get("call", payload)
    extracted = call_data.get("call_analysis", {}).get("custom_analysis_data", call_data)

    job = Job(
        job_id=call_data.get("call_id", "unknown")[:8],
        customer=Customer(
            name=extracted.get("caller_name", ""),
            phone=extracted.get("phone_number", ""),
            address=extracted.get("location", ""),
        ),
        trade=Trade.HVAC if "ac" in extracted.get("service_need", "").lower()
              or "hvac" in extracted.get("service_need", "").lower()
              or "furnace" in extracted.get("service_need", "").lower()
              else Trade.PLUMBING,
        description=extracted.get("service_need", ""),
        urgency=_urgency_from_payload(extracted),
    )
    job.log("Job created from Retell webhook")

    if extracted.get("disqualification_reason"):
        job.log(f"Disqualified: {extracted['disqualification_reason']}")
        return jsonify({"status": "disqualified", "job_id": job.job_id}), 200

    result = handle_job(job, BUSINESS, OWNER_PHONE)

    return jsonify({
        "status": result.status.value,
        "job_id": result.job_id,
        "assigned_tech": result.assigned_tech.name if result.assigned_tech else None,
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "hashtag-dispatch"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
