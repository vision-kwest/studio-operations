from __future__ import annotations

from studio_operations.models import HealthStatus, Resource


def assess(resource: Resource) -> Resource:
    reasons = []
    status = HealthStatus.HEALTHY
    if resource.expired:
        status = HealthStatus.CRITICAL
        reasons.append("Deployment has expired")
    if resource.type == "EC2 Instance" and resource.state == "stopped":
        status = max(status, HealthStatus.WARNING, key=_rank)
        reasons.append("Workstation is stopped")
    if resource.type == "EBS Volume" and not resource.metadata.get("attachments"):
        status = max(status, HealthStatus.WARNING, key=_rank)
        reasons.append("Volume is unattached")
    if resource.type == "EFS" and not resource.metadata.get("mount_targets"):
        status = max(status, HealthStatus.CRITICAL, key=_rank)
        reasons.append("EFS has no mount targets")
    if (
        resource.type == "EC2 Instance"
        and resource.tags.get("Profile", "").lower().startswith("control")
        and not resource.metadata.get("role")
    ):
        status = max(status, HealthStatus.CRITICAL, key=_rank)
        reasons.append("Control workstation has no IAM profile")
    resource.health = status
    resource.health_reasons = reasons
    return resource


def _rank(status: HealthStatus) -> int:
    return {HealthStatus.HEALTHY: 0, HealthStatus.WARNING: 1, HealthStatus.CRITICAL: 2}[status]


def assess_all(resources: list[Resource]) -> list[Resource]:
    return [assess(item) for item in resources]
