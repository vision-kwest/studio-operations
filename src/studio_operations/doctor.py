from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError


@dataclass(slots=True)
class Check:
    name: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def run_checks(session: Any) -> list[Check]:
    region = session.region_name or "us-east-1"
    checks: list[tuple[str, Callable[[], Any]]] = [
        ("AWS authentication", lambda: session.client("sts").get_caller_identity()),
        (
            "Resource Explorer",
            lambda: session.client("resource-explorer-2", region_name=region).list_indexes(),
        ),
        (
            "Resource Groups",
            lambda: session.client("resource-groups", region_name=region).list_groups(),
        ),
        (
            "Cost Explorer",
            lambda: session.client("ce", region_name="us-east-1").get_cost_and_usage(
                TimePeriod={"Start": "2026-01-01", "End": "2026-01-02"},
                Granularity="DAILY",
                Metrics=["UnblendedCost"],
            ),
        ),
        (
            "Inventory permissions",
            lambda: session.client("ec2", region_name=region).describe_instances(MaxResults=5),
        ),
    ]
    result = []
    for name, call in checks:
        try:
            call()
            result.append(Check(name, True, "available"))
        except (BotoCoreError, ClientError) as exc:
            result.append(Check(name, False, str(exc)))
    return result
