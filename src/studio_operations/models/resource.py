from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class HealthStatus(StrEnum):
    HEALTHY = "Healthy"
    WARNING = "Warning"
    CRITICAL = "Critical"


class ChargeCategory(StrEnum):
    RUNNING = "Running"
    STOPPED = "Stopped"
    STORAGE = "Storage"
    NETWORKING = "Networking"
    UNKNOWN = "Unknown"


@dataclass(slots=True)
class ResourceCost:
    current: float | None = None
    estimated_monthly: float | None = None
    category: ChargeCategory = ChargeCategory.UNKNOWN
    currency: str = "USD"


@dataclass(slots=True)
class Resource:
    id: str
    type: str
    region: str
    name: str = ""
    owner: str = ""
    deployment_id: str = ""
    repository: str = ""
    environment: str = ""
    created: datetime | None = None
    expires: datetime | None = None
    state: str = "unknown"
    tags: dict[str, str] = field(default_factory=dict)
    health: HealthStatus = HealthStatus.HEALTHY
    health_reasons: list[str] = field(default_factory=list)
    cost: ResourceCost = field(default_factory=ResourceCost)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def expired(self) -> bool:
        return bool(self.expires and self.expires <= datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        for key in ("created", "expires"):
            value[key] = value[key].isoformat() if value[key] else None
        value["health"] = self.health.value
        value["cost"]["category"] = self.cost.category.value
        return value


# Resource-specific aliases preserve a strongly typed public vocabulary while sharing fields.
EC2Instance = EBSVolume = IAMRole = SecurityGroup = Resource
