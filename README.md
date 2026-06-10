# SIM Swap OTP Lab

A closed, synthetic cybersecurity training lab that demonstrates a common OTP control failure:

> The application sends an SMS OTP without checking whether the mobile number was recently SIM-swapped, ported, or associated with a risky device event.

This lab is designed for defensive training, secure coding workshops, application security testing, and fraud-risk awareness sessions.

## What learners do

Learners enter a mobile number into a web form and compare two processing modes:

| Mode | Behaviour |
|---|---|
| Secure mode | Checks mobile-number risk before sending OTP |
| Vulnerable mode | Sends OTP blindly without checking SIM swap, porting, or device-risk state |

No real SMS is sent. OTPs are captured in a local in-memory OTP sink.

## Test numbers

| Number | Scenario | Expected secure behaviour |
|---|---|---|
| `+27720000001` | Low risk number | OTP allowed |
| `+27720000002` | SIM swapped 2 hours ago | OTP blocked |
| `+27720000003` | Number ported 20 hours ago | OTP blocked |
| `+27720000004` | Device changed 30 minutes ago | Step-up required |
| `+27720000005` | Old SIM swap outside 72-hour window | OTP allowed |

## Run with Docker Compose

```bash
docker compose up --build
```

Open:

```text
http://localhost:8000
```

## Run with Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

```text
http://localhost:8000
```

## Run tests

```bash
pytest -q
```

## API examples

### Secure mode: recent SIM swap should be blocked

```bash
curl -X POST http://localhost:8000/api/request-otp \
  -H "Content-Type: application/json" \
  -d '{"mobile":"+27720000002","mode":"secure"}'
```

Expected result:

```json
{
  "status": "OTP_BLOCKED",
  "mode": "secure",
  "reason": "RECENT_SIM_SWAP"
}
```

### Vulnerable mode: recent SIM swap still receives OTP

```bash
curl -X POST http://localhost:8000/api/request-otp \
  -H "Content-Type: application/json" \
  -d '{"mobile":"+27720000002","mode":"vulnerable"}'
```

Expected vulnerable result:

```json
{
  "status": "OTP_SENT",
  "mode": "vulnerable",
  "reason": "NO_RISK_CHECK_PERFORMED"
}
```

### View captured OTPs

```bash
curl http://localhost:8000/api/messages
```

### Reset the lab state

```bash
curl -X DELETE http://localhost:8000/api/reset
```

## Key learning point

The vulnerability is not merely that OTP exists. The vulnerability is that the application treats the mobile number as a trusted possession factor without checking whether control of that number recently changed.

## Secure decision policy

| Risk signal | Threshold | Decision |
|---|---:|---|
| SIM swap | Less than 72 hours | Block SMS OTP |
| Number port | Less than 72 hours | Block SMS OTP |
| Device change | Less than 24 hours | Require step-up |
| No recent risk event | N/A | Allow OTP |

## Safe-use rules

- Do not use real customer data.
- Do not use real mobile numbers beyond synthetic training examples.
- Do not integrate a live SMS gateway.
- Do not connect this lab to real telco, banking, or identity infrastructure.
- Do not use this lab to test third-party systems without written authorization.

## Suggested workshop flow

1. Learner tests `+27720000001` in secure mode and observes that OTP is allowed.
2. Learner tests `+27720000002` in secure mode and observes that OTP is blocked.
3. Learner tests `+27720000002` in vulnerable mode and observes that OTP is sent.
4. Learner explains why sending OTP after recent SIM swap is a control failure.
5. Learner reviews `evaluate_mobile_risk()` in `app/main.py`.
6. Learner changes the policy thresholds and runs `pytest -q`.

## GitHub Codespaces

This repo includes a `.devcontainer/devcontainer.json`. In GitHub Codespaces:

1. Open the repository.
2. Click **Code**.
3. Choose **Codespaces**.
4. Create a new Codespace.
5. Run:

```bash
docker compose up --build
```

6. Open the forwarded port `8000`.

## Repository structure

```text
sim-swap-otp-lab/
├── app/
│   ├── main.py
│   └── templates/
│       └── index.html
├── docs/
│   ├── instructor-guide.md
│   └── learner-guide.md
├── tests/
│   └── test_policy.py
├── .devcontainer/
│   └── devcontainer.json
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── SECURITY.md
└── README.md
```
