# Security Policy

This repository is a defensive cybersecurity training lab.

## Safe-use rules

- Use synthetic numbers only.
- Do not connect the lab to a live SMS provider.
- Do not connect the lab to production telco, banking, or identity systems.
- Do not test against real mobile operators or real subscriber data.
- Do not store secrets, API keys, customer records, or production credentials in this repo.

## What this lab demonstrates

The lab demonstrates a control failure where an application sends an OTP without first evaluating recent mobile-number risk events such as:

- SIM swap
- Number porting
- Recent device change

## Reporting concerns

Open a GitHub issue for defects in the lab implementation, documentation, or training flow.
