"""SIM Swap OTP Lab.

A defensive cybersecurity training application that demonstrates a common OTP
control failure: sending an SMS OTP without first checking whether the mobile
number was recently SIM-swapped, ported, or associated with a risky device event.

All numbers and OTPs are synthetic. This application must not be connected to a
real SMS provider or production telco risk API.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

app = FastAPI(
    title="SIM Swap OTP Lab",
    description="Closed, synthetic lab for demonstrating OTP risk decisions after SIM swap or porting events.",
    version="1.0.0",
)

templates = Jinja2Templates(directory="app/templates")

NOW = datetime.now(timezone.utc)
COOLING_OFF_HOURS = 72
DEVICE_CHANGE_STEP_UP_HOURS = 24


class ProcessingMode(str, Enum):
    secure = "secure"
    vulnerable = "vulnerable"


class Decision(str, Enum):
    allow = "ALLOW"
    block = "BLOCK"
    step_up = "STEP_UP"


class OtpApiRequest(BaseModel):
    mobile: str = Field(..., examples=["+27720000002"])
    mode: ProcessingMode = ProcessingMode.secure


RISK_DB: dict[str, dict[str, Any]] = {
    "+27720000001": {
        "name": "Alice",
        "scenario": "Low risk number",
        "sim_swap_at": None,
        "ported_at": None,
        "device_change_at": None,
    },
    "+27720000002": {
        "name": "Bob",
        "scenario": "SIM swapped 2 hours ago",
        "sim_swap_at": NOW - timedelta(hours=2),
        "ported_at": None,
        "device_change_at": None,
    },
    "+27720000003": {
        "name": "Carol",
        "scenario": "Number ported 20 hours ago",
        "sim_swap_at": None,
        "ported_at": NOW - timedelta(hours=20),
        "device_change_at": None,
    },
    "+27720000004": {
        "name": "Dave",
        "scenario": "Device changed 30 minutes ago",
        "sim_swap_at": None,
        "ported_at": None,
        "device_change_at": NOW - timedelta(minutes=30),
    },
    "+27720000005": {
        "name": "Eve",
        "scenario": "Old SIM swap outside the 72-hour cooling-off window",
        "sim_swap_at": NOW - timedelta(days=10),
        "ported_at": None,
        "device_change_at": None,
    },
}

SMS_SINK: list[dict[str, Any]] = []
AUDIT_LOG: list[dict[str, Any]] = []


def iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def hours_since(timestamp: datetime | None) -> float | None:
    if timestamp is None:
        return None
    now = datetime.now(timezone.utc)
    return round((now - timestamp).total_seconds() / 3600, 2)


def normalise_mobile(mobile: str) -> str:
    return mobile.strip().replace(" ", "")


def get_mobile_risk(mobile: str) -> dict[str, Any]:
    mobile = normalise_mobile(mobile)
    record = RISK_DB.get(mobile)

    if not record:
        return {
            "known_number": False,
            "mobile": mobile,
            "name": "Unknown",
            "scenario": "Unknown number in training dataset",
            "sim_swap_at": None,
            "ported_at": None,
            "device_change_at": None,
            "sim_swap_age_hours": None,
            "ported_age_hours": None,
            "device_change_age_hours": None,
        }

    return {
        "known_number": True,
        "mobile": mobile,
        "name": record["name"],
        "scenario": record["scenario"],
        "sim_swap_at": iso_or_none(record["sim_swap_at"]),
        "ported_at": iso_or_none(record["ported_at"]),
        "device_change_at": iso_or_none(record["device_change_at"]),
        "sim_swap_age_hours": hours_since(record["sim_swap_at"]),
        "ported_age_hours": hours_since(record["ported_at"]),
        "device_change_age_hours": hours_since(record["device_change_at"]),
    }


def evaluate_mobile_risk(mobile: str) -> dict[str, Any]:
    risk = get_mobile_risk(mobile)

    sim_swap_hours = risk["sim_swap_age_hours"]
    ported_hours = risk["ported_age_hours"]
    device_change_hours = risk["device_change_age_hours"]

    if sim_swap_hours is not None and sim_swap_hours < COOLING_OFF_HOURS:
        return {
            "allow_sms_otp": False,
            "decision": Decision.block,
            "reason": "RECENT_SIM_SWAP",
            "control": f"Block SMS OTP for {COOLING_OFF_HOURS} hours after SIM swap.",
            "risk_signal": risk,
        }

    if ported_hours is not None and ported_hours < COOLING_OFF_HOURS:
        return {
            "allow_sms_otp": False,
            "decision": Decision.block,
            "reason": "RECENT_NUMBER_PORT",
            "control": f"Block SMS OTP for {COOLING_OFF_HOURS} hours after number porting.",
            "risk_signal": risk,
        }

    if device_change_hours is not None and device_change_hours < DEVICE_CHANGE_STEP_UP_HOURS:
        return {
            "allow_sms_otp": False,
            "decision": Decision.step_up,
            "reason": "RECENT_DEVICE_CHANGE",
            "control": f"Require step-up authentication for {DEVICE_CHANGE_STEP_UP_HOURS} hours after device change.",
            "risk_signal": risk,
        }

    return {
        "allow_sms_otp": True,
        "decision": Decision.allow,
        "reason": "LOW_RISK",
        "control": "Allow SMS OTP because no recent high-risk mobile event was detected.",
        "risk_signal": risk,
    }


def send_otp_to_sink(mobile: str) -> dict[str, Any]:
    otp = f"{random.randint(100000, 999999)}"
    message = {
        "mobile": normalise_mobile(mobile),
        "otp": otp,
        "message": f"Training lab OTP: {otp}",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    SMS_SINK.append(message)
    return message


def audit_event(mobile: str, mode: str, result: dict[str, Any]) -> None:
    AUDIT_LOG.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mobile": normalise_mobile(mobile),
            "mode": mode,
            "status": result.get("status"),
            "reason": result.get("reason"),
            "decision": result.get("decision"),
        }
    )


def process_otp_request(mobile: str, mode: ProcessingMode) -> dict[str, Any]:
    mobile = normalise_mobile(mobile)
    risk_decision = evaluate_mobile_risk(mobile)

    if mode == ProcessingMode.vulnerable:
        send_otp_to_sink(mobile)
        result = {
            "status": "OTP_SENT",
            "mode": "vulnerable",
            "decision": "ALLOW_WITHOUT_RISK_CHECK",
            "reason": "NO_RISK_CHECK_PERFORMED",
            "teaching_point": "This is the bug: OTP was sent without checking SIM swap, porting, or device-risk state.",
            "risk_signal": risk_decision["risk_signal"],
        }
        audit_event(mobile, mode.value, result)
        return result

    if risk_decision["allow_sms_otp"]:
        send_otp_to_sink(mobile)
        result = {
            "status": "OTP_SENT",
            "mode": "secure",
            "decision": risk_decision["decision"],
            "reason": risk_decision["reason"],
            "control": risk_decision["control"],
            "teaching_point": "OTP was allowed because no recent high-risk mobile event was found.",
            "risk_signal": risk_decision["risk_signal"],
        }
        audit_event(mobile, mode.value, result)
        return result

    result = {
        "status": "OTP_BLOCKED" if risk_decision["decision"] == Decision.block else "STEP_UP_REQUIRED",
        "mode": "secure",
        "decision": risk_decision["decision"],
        "reason": risk_decision["reason"],
        "control": risk_decision["control"],
        "recommended_action": "Use passkey, authenticator app, banking-app push, manual review, or a cooling-off period.",
        "risk_signal": risk_decision["risk_signal"],
    }
    audit_event(mobile, mode.value, result)
    return result


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "messages": SMS_SINK,
            "audit_log": AUDIT_LOG,
            "numbers": [get_mobile_risk(number) for number in RISK_DB.keys()],
        },
    )


@app.post("/process", response_class=HTMLResponse)
def process(
    request: Request,
    mobile: str = Form(...),
    mode: ProcessingMode = Form(ProcessingMode.secure),
):
    result = process_otp_request(mobile, mode)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "messages": SMS_SINK,
            "audit_log": AUDIT_LOG,
            "numbers": [get_mobile_risk(number) for number in RISK_DB.keys()],
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/risk-catalog")
def api_risk_catalog():
    return [get_mobile_risk(number) for number in RISK_DB.keys()]


@app.get("/api/risk/{mobile}")
def api_risk(mobile: str):
    return get_mobile_risk(mobile)


@app.post("/api/request-otp")
def api_request_otp(payload: OtpApiRequest):
    return process_otp_request(payload.mobile, payload.mode)


@app.get("/api/messages")
def api_messages():
    return SMS_SINK


@app.get("/api/audit-log")
def api_audit_log():
    return AUDIT_LOG


@app.delete("/api/reset")
def reset_lab_state():
    SMS_SINK.clear()
    AUDIT_LOG.clear()
    return {"status": "CLEARED"}
