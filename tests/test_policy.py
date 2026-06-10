from fastapi.testclient import TestClient

from app.main import app, evaluate_mobile_risk

client = TestClient(app)


def test_low_risk_number_allows_sms_otp():
    decision = evaluate_mobile_risk("+27720000001")
    assert decision["allow_sms_otp"] is True
    assert decision["reason"] == "LOW_RISK"


def test_recent_sim_swap_blocks_sms_otp():
    decision = evaluate_mobile_risk("+27720000002")
    assert decision["allow_sms_otp"] is False
    assert decision["decision"] == "BLOCK"
    assert decision["reason"] == "RECENT_SIM_SWAP"


def test_recent_number_port_blocks_sms_otp():
    decision = evaluate_mobile_risk("+27720000003")
    assert decision["allow_sms_otp"] is False
    assert decision["decision"] == "BLOCK"
    assert decision["reason"] == "RECENT_NUMBER_PORT"


def test_recent_device_change_requires_step_up():
    decision = evaluate_mobile_risk("+27720000004")
    assert decision["allow_sms_otp"] is False
    assert decision["decision"] == "STEP_UP"
    assert decision["reason"] == "RECENT_DEVICE_CHANGE"


def test_old_sim_swap_outside_cooling_off_allows_otp():
    decision = evaluate_mobile_risk("+27720000005")
    assert decision["allow_sms_otp"] is True
    assert decision["reason"] == "LOW_RISK"


def test_secure_api_blocks_recent_sim_swap():
    client.delete("/api/reset")
    response = client.post(
        "/api/request-otp",
        json={"mobile": "+27720000002", "mode": "secure"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OTP_BLOCKED"
    assert body["reason"] == "RECENT_SIM_SWAP"

    messages = client.get("/api/messages").json()
    assert messages == []


def test_vulnerable_api_sends_otp_after_recent_sim_swap():
    client.delete("/api/reset")
    response = client.post(
        "/api/request-otp",
        json={"mobile": "+27720000002", "mode": "vulnerable"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OTP_SENT"
    assert body["reason"] == "NO_RISK_CHECK_PERFORMED"

    messages = client.get("/api/messages").json()
    assert len(messages) == 1
    assert messages[0]["mobile"] == "+27720000002"
