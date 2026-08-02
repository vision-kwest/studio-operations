from __future__ import annotations

from dataclasses import dataclass

from studio_operations.models import Resource


@dataclass(frozen=True, slots=True)
class CleanupAction:
    resource_id: str
    resource_type: str
    reason: str
    action: str

    def to_dict(self) -> dict[str, str]:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "reason": self.reason,
            "action": self.action,
        }


def plan_cleanup(resources: list[Resource]) -> list[CleanupAction]:
    actions = []
    for item in resources:
        reason = None
        if item.expired:
            reason = "Expired deployment"
        elif item.type == "EBS Volume" and not item.metadata.get("attachments"):
            reason = "Detached EBS volume"
        elif item.type == "EC2 Instance" and item.state == "stopped":
            reason = "Stopped workstation"
        elif item.type == "EFS" and not item.metadata.get("mount_targets"):
            reason = "Unused EFS"
        elif item.type == "CloudWatch Log Group" and item.metadata.get("retention_days") is None:
            reason = "Log group has no retention policy"
        if reason:
            actions.append(CleanupAction(item.id, item.type, reason, "delete"))
    return actions
