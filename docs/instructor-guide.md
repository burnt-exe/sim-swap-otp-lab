# Instructor Guide: SIM Swap OTP Lab

## Training outcome

Learners should understand that SMS OTP delivery must be guarded by a risk decision layer. The target defect is:

> OTP is delivered even though the mobile number was recently SIM-swapped, ported, or associated with a risky device event.

## Recommended timing

| Segment | Duration |
|---|---:|
| Context: SIM swap fraud and OTP risk | 10 minutes |
| Lab walkthrough | 10 minutes |
| Learner exercises | 25 minutes |
| Secure design discussion | 15 minutes |
| Assessment and debrief | 10 minutes |

## Demonstration script

1. Show `+27720000001` in secure mode. OTP is sent.
2. Show `+27720000002` in secure mode. OTP is blocked.
3. Show `+27720000002` in vulnerable mode. OTP is sent.
4. Explain that vulnerable mode simulates missing risk checks before OTP delivery.
5. Review `evaluate_mobile_risk()` in `app/main.py`.
6. Run `pytest -q` to show the policy tests.

## Debrief question bank

- Is SMS OTP always insecure, or is the risk contextual?
- What changes after a SIM swap or number porting event?
- Why is a cooling-off period useful?
- What should happen for high-value transactions?
- How should the user be notified if SMS is considered compromised?
- Which MFA methods provide stronger phishing and account-takeover resistance?

## Assessment rubric

| Competency | Evidence |
|---|---|
| Identifies the bug | Learner explains that vulnerable mode sends OTP without a mobile-risk check. |
| Understands risk signals | Learner can distinguish SIM swap, porting, and device-change events. |
| Applies secure policy | Learner can explain block, step-up, and allow decisions. |
| Interprets logs | Learner can use the OTP sink and audit log to support the finding. |
| Recommends remediation | Learner proposes passkeys, authenticator apps, banking-app push, manual review, or cooling-off. |

## Safe facilitation notes

- Keep the lab synthetic.
- Do not connect a real SMS gateway.
- Do not use real subscriber data.
- Do not demonstrate attacks against carrier, bank, or identity-provider systems.
- Keep the focus on defensive control design and secure engineering.
