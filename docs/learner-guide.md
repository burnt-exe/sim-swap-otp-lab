# Learner Guide: SIM Swap OTP Lab

## Objective

Demonstrate why an application should not send SMS OTPs blindly after recent mobile-number risk events such as SIM swap, number porting, or device change.

## Exercise 1: Low-risk number

1. Open the lab web UI.
2. Enter `+27720000001`.
3. Select **Secure mode**.
4. Submit the request.

Expected result: `OTP_SENT` with reason `LOW_RISK`.

## Exercise 2: Recent SIM swap

1. Enter `+27720000002`.
2. Select **Secure mode**.
3. Submit the request.

Expected result: `OTP_BLOCKED` with reason `RECENT_SIM_SWAP`.

Discussion questions:

- Why should SMS OTP be blocked after a recent SIM swap?
- Which alternative authentication factors would be safer?
- What audit fields would a fraud analyst need?

## Exercise 3: Vulnerable behaviour

1. Enter `+27720000002`.
2. Select **Vulnerable mode**.
3. Submit the request.
4. Review the local OTP sink.

Expected result: `OTP_SENT` even though the number was recently SIM-swapped.

This is the simulated bug.

## Exercise 4: Number porting

1. Enter `+27720000003`.
2. Select **Secure mode**.
3. Submit the request.

Expected result: `OTP_BLOCKED` with reason `RECENT_NUMBER_PORT`.

## Exercise 5: Device change

1. Enter `+27720000004`.
2. Select **Secure mode**.
3. Submit the request.

Expected result: `STEP_UP_REQUIRED` with reason `RECENT_DEVICE_CHANGE`.

## Stretch task

Modify `app/main.py` so that unknown numbers require step-up instead of being treated as low risk. Then add a unit test for your new policy.
