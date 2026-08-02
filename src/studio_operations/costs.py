from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any


@dataclass(slots=True)
class CostSummary:
    current_month: float
    estimated_monthly: float
    daily: list[dict[str, str]]
    by_project: list[dict[str, str]]
    by_deployment: list[dict[str, str]]
    by_owner: list[dict[str, str]]
    currency: str = "USD"

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_month": self.current_month,
            "estimated_monthly": self.estimated_monthly,
            "currency": self.currency,
            "daily": self.daily,
            "per_project": self.by_project,
            "per_deployment": self.by_deployment,
            "per_owner": self.by_owner,
        }


def _groups(client: Any, start: str, end: str, tag: str) -> list[dict[str, str]]:
    response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "TAG", "Key": tag}],
    )
    return [
        {
            "name": g["Keys"][0].removeprefix(f"{tag}$") or "Untagged",
            "amount": g["Metrics"]["UnblendedCost"]["Amount"],
        }
        for result in response.get("ResultsByTime", [])
        for g in result.get("Groups", [])
    ]


def get_costs(session: Any) -> CostSummary:
    client = session.client("ce", region_name="us-east-1")
    today = date.today()
    start = today.replace(day=1).isoformat()
    end = (today + timedelta(days=1)).isoformat()
    daily_response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end}, Granularity="DAILY", Metrics=["UnblendedCost"]
    )
    daily = [
        {"date": x["TimePeriod"]["Start"], "amount": x["Total"]["UnblendedCost"]["Amount"]}
        for x in daily_response.get("ResultsByTime", [])
    ]
    total = sum(float(x["amount"]) for x in daily)
    elapsed = max(today.day, 1)
    estimate = (
        total
        / elapsed
        * ((today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)).day
    )
    return CostSummary(
        total,
        estimate,
        daily,
        _groups(client, start, end, "Project"),
        _groups(client, start, end, "DeploymentID"),
        _groups(client, start, end, "Owner"),
    )
