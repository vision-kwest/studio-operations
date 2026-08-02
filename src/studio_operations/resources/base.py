from __future__ import annotations

from datetime import datetime
from typing import Any

from studio_operations.models import Resource
from studio_operations.tags import normalize_tags, parse_time


def resource(
    resource_id: str,
    kind: str,
    region: str,
    raw_tags: Any = None,
    *,
    state: str = "unknown",
    created: datetime | None = None,
    metadata: dict[str, Any] | None = None,
) -> Resource:
    tags = normalize_tags(raw_tags)
    return Resource(
        id=resource_id,
        type=kind,
        region=region,
        name=tags.get("Name", resource_id),
        owner=tags.get("Owner", ""),
        deployment_id=tags.get("DeploymentID", ""),
        repository=tags.get("Repository", ""),
        environment=tags.get("Environment", ""),
        created=created or parse_time(tags.get("CreationTime")),
        expires=parse_time(tags.get("ExpirationTime")),
        state=state,
        tags=tags,
        metadata=metadata or {},
    )
