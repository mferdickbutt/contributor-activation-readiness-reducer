#!/usr/bin/env python3
"""
Deterministic reducer for sanitized pre-first-task contributor activation receipts.

The artifact is self-contained, dependency-free, and intentionally scoped to
activation readiness before a contributor receives a first task. It does not
model offer lifecycle dropoff, refusal reasons, reward adjudication, or live
onboarding dashboards.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable, Iterable


@dataclass(frozen=True)
class ActivationReceipt:
    """Sanitized receipt with only non-identifying activation-readiness signals."""

    fixture_id: str
    account_age_days: int
    wallet_connected: bool
    profile_signal: str
    first_task_request_state: str
    capability_evidence: str
    verification_readiness: str
    privacy_risk: str
    freshness_days: int


@dataclass(frozen=True)
class ActivationDecision:
    activation_decision: str
    severity: int
    reason_code: str


DecisionRule = tuple[Callable[[ActivationReceipt], bool], ActivationDecision]


DECISION_RULES: tuple[DecisionRule, ...] = (
    (
        lambda receipt: receipt.privacy_risk == "blocking",
        ActivationDecision("privacy-blocked", 95, "privacy-risk-blocking"),
    ),
    (
        lambda receipt: receipt.freshness_days > 45
        or receipt.capability_evidence == "conflicting"
        or receipt.privacy_risk == "elevated",
        ActivationDecision("reviewer-escalation", 90, "manual-review-required"),
    ),
    (
        lambda receipt: receipt.wallet_connected
        and receipt.profile_signal == "absent"
        and receipt.first_task_request_state == "none"
        and receipt.capability_evidence == "none",
        ActivationDecision("wallet-only", 70, "wallet-only-no-activation-signal"),
    ),
    (
        lambda receipt: receipt.profile_signal in {"absent", "minimal"},
        ActivationDecision("missing-profile-signal", 65, "profile-signal-insufficient"),
    ),
    (
        lambda receipt: receipt.first_task_request_state == "none",
        ActivationDecision("no-first-task-request", 55, "first-task-request-missing"),
    ),
    (
        lambda receipt: receipt.capability_evidence in {"none", "vague"},
        ActivationDecision("unclear-capability", 50, "capability-evidence-unclear"),
    ),
    (
        lambda receipt: receipt.verification_readiness != "ready",
        ActivationDecision("verification-unready", 45, "verification-not-ready"),
    ),
    (
        lambda receipt: True,
        ActivationDecision("ready-for-first-task", 10, "activation-ready"),
    ),
)


FIXTURE_RECEIPTS: tuple[ActivationReceipt, ...] = (
    ActivationReceipt(
        fixture_id="CAR-001",
        account_age_days=1,
        wallet_connected=True,
        profile_signal="absent",
        first_task_request_state="none",
        capability_evidence="none",
        verification_readiness="unready",
        privacy_risk="none",
        freshness_days=1,
    ),
    ActivationReceipt(
        fixture_id="CAR-002",
        account_age_days=4,
        wallet_connected=False,
        profile_signal="minimal",
        first_task_request_state="submitted",
        capability_evidence="specific",
        verification_readiness="ready",
        privacy_risk="none",
        freshness_days=2,
    ),
    ActivationReceipt(
        fixture_id="CAR-003",
        account_age_days=8,
        wallet_connected=True,
        profile_signal="specific",
        first_task_request_state="none",
        capability_evidence="specific",
        verification_readiness="ready",
        privacy_risk="none",
        freshness_days=3,
    ),
    ActivationReceipt(
        fixture_id="CAR-004",
        account_age_days=3,
        wallet_connected=True,
        profile_signal="specific",
        first_task_request_state="submitted",
        capability_evidence="vague",
        verification_readiness="ready",
        privacy_risk="none",
        freshness_days=1,
    ),
    ActivationReceipt(
        fixture_id="CAR-005",
        account_age_days=6,
        wallet_connected=True,
        profile_signal="specific",
        first_task_request_state="submitted",
        capability_evidence="specific",
        verification_readiness="pending",
        privacy_risk="none",
        freshness_days=4,
    ),
    ActivationReceipt(
        fixture_id="CAR-006",
        account_age_days=2,
        wallet_connected=True,
        profile_signal="specific",
        first_task_request_state="submitted",
        capability_evidence="specific",
        verification_readiness="ready",
        privacy_risk="blocking",
        freshness_days=1,
    ),
    ActivationReceipt(
        fixture_id="CAR-007",
        account_age_days=5,
        wallet_connected=True,
        profile_signal="specific",
        first_task_request_state="submitted",
        capability_evidence="specific",
        verification_readiness="ready",
        privacy_risk="none",
        freshness_days=2,
    ),
    ActivationReceipt(
        fixture_id="CAR-008",
        account_age_days=67,
        wallet_connected=True,
        profile_signal="specific",
        first_task_request_state="submitted",
        capability_evidence="conflicting",
        verification_readiness="ready",
        privacy_risk="none",
        freshness_days=61,
    ),
)


def reduce_activation_receipt(receipt: ActivationReceipt) -> dict[str, object]:
    """Return exactly one deterministic activation-readiness decision."""

    for predicate, decision in DECISION_RULES:
        if predicate(receipt):
            return {
                "fixture_id": receipt.fixture_id,
                "activation_decision": decision.activation_decision,
                "severity": decision.severity,
                "reason_code": decision.reason_code,
            }
    raise RuntimeError("unreachable decision state")


def reduce_activation_receipts(
    receipts: Iterable[ActivationReceipt],
) -> list[dict[str, object]]:
    """Reduce receipts in fixture-id order for byte-stable reviewer output."""

    return [
        reduce_activation_receipt(receipt)
        for receipt in sorted(receipts, key=lambda item: item.fixture_id)
    ]


def main() -> None:
    print(json.dumps(reduce_activation_receipts(FIXTURE_RECEIPTS), indent=2))


if __name__ == "__main__":
    main()
