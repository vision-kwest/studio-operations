from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from typing import Any

STANDARD_TAGS = (
    "Project",
    "Repository",
    "DeploymentID",
    "Environment",
    "Owner",
    "ManagedBy",
    "Version",
    "Profile",
    "CreationTime",
    "ExpirationTime",
)


def normalize_tags(tags: Mapping[str, Any] | Iterable[Mapping[str, Any]] | None) -> dict[str, str]:
    """Normalize both AWS tag-list and mapping representations."""
    if tags is None:
        return {}
    if isinstance(tags, Mapping):
        return {str(k): str(v) for k, v in tags.items() if v is not None}
    return {
        str(tag["Key"]): str(tag.get("Value", "")) for tag in tags if tag.get("Key") is not None
    }


def parse_time(value: str | datetime | None) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


def missing_standard_tags(tags: Mapping[str, str]) -> list[str]:
    return [key for key in STANDARD_TAGS if not tags.get(key)]
