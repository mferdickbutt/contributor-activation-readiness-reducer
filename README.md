# Contributor Activation Readiness Reducer

A self-contained Python reducer for sanitized new-contributor activation receipts. It emits one deterministic pre-first-task activation-readiness decision per case so idle new accounts can be reviewed without relying on opaque judgment.

## Scope

This artifact covers only the activation surface before a contributor receives a first task:

- wallet-only accounts
- missing profile signal
- missing first-task request
- unclear capability evidence
- verification readiness gaps
- privacy-blocked receipts
- ready-for-first-task receipts
- reviewer escalation

It intentionally does not cover offer lifecycle dropoff, refusal normalization, reward adjudication, live wallets, credentials, proprietary records, private profile text, or onboarding dashboards.

## Usage

Run with Python 3.11 or newer. No dependencies or external services are required.

```bash
python contributor_activation_readiness_reducer.py
```

The script prints a deterministic JSON array sorted by `fixture_id`. Each item contains exactly these keys:

- `fixture_id`
- `activation_decision`
- `severity`
- `reason_code`

## Decision Routes

The reducer emits exactly one of these decisions per receipt:

- `wallet-only`
- `missing-profile-signal`
- `no-first-task-request`
- `unclear-capability`
- `verification-unready`
- `privacy-blocked`
- `ready-for-first-task`
- `reviewer-escalation`

Rule precedence is explicit in `DECISION_RULES`: blocking privacy risk is handled first, reviewer escalation follows for stale, conflicting, or elevated-risk receipts, then activation gaps are evaluated from account-surface gaps toward readiness.

## Sanitized Receipt Shape

Each embedded fixture uses non-identifying fields only:

- account age in days
- whether a wallet was connected, without wallet identifiers
- profile signal category
- first-task request state
- capability evidence category
- verification readiness category
- privacy risk category
- freshness age in days

The fixture IDs are generic (`CAR-001` through `CAR-008`) and contain no live wallets, usernames, credentials, proprietary records, private profile text, or customer data.

## Verification Contract

The embedded fixtures exercise all eight decision routes. A reviewer can verify the artifact by running the script and checking that the output contains at least eight cases, each with exactly one activation decision and one reason code.

## Dependency Posture

The reducer uses only the Python standard library: `dataclasses`, `json`, and `typing`.
