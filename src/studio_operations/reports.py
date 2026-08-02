from __future__ import annotations

import json
from typing import Any

from studio_operations.inventory import group_resources
from studio_operations.models import Resource

COLUMNS = (
    "Name",
    "Region",
    "Owner",
    "Deployment ID",
    "Repository",
    "Environment",
    "Creation Time",
    "Expiration",
    "Current State",
    "Health",
    "Tags",
)


def inventory_data(resources: list[Resource]) -> dict[str, Any]:
    return {
        group: {kind: [item.to_dict() for item in items] for kind, items in kinds.items()}
        for group, kinds in group_resources(resources).items()
    }


def render_json(value: Any) -> str:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    return json.dumps(value, indent=2, sort_keys=True, default=str) + "\n"


def render_inventory(resources: list[Resource], markdown: bool = False) -> str:
    lines = ["# Infrastructure" if markdown else "Infrastructure"]
    for group, kinds in group_resources(resources).items():
        lines.extend([f"\n## {group}" if markdown else f"\n{group}"])
        for kind, items in kinds.items():
            lines.append(f"\n### {kind}" if markdown else f"  {kind}")
            if markdown:
                lines += ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
            for item in items:
                values = (
                    item.name,
                    item.region,
                    item.owner or "-",
                    item.deployment_id or "-",
                    item.repository or "-",
                    item.environment or "-",
                    item.created.isoformat() if item.created else "-",
                    item.expires.isoformat() if item.expires else "-",
                    item.state,
                    item.health.value,
                    ", ".join(f"{k}={v}" for k, v in sorted(item.tags.items())) or "-",
                )
                lines.append(
                    "| " + " | ".join(values) + " |" if markdown else "    " + " | ".join(values)
                )
    return "\n".join(lines) + "\n"
