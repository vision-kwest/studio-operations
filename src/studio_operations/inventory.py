from __future__ import annotations

from collections import defaultdict

from studio_operations.models import Resource

GROUPS = {
    "EC2 Instance": "Compute",
    "EBS Volume": "Storage",
    "EFS": "Storage",
    "S3 Bucket": "Storage",
    "Security Group": "Networking",
    "Key Pair": "Networking",
    "IAM Role": "IAM",
    "CloudWatch Log Group": "Monitoring",
    "CodeBuild Project": "Automation",
    "EventBridge Rule": "Automation",
    "Lambda Function": "Automation",
}


def group_resources(resources: list[Resource]) -> dict[str, dict[str, list[Resource]]]:
    grouped: dict[str, dict[str, list[Resource]]] = defaultdict(lambda: defaultdict(list))
    for item in resources:
        subgroup = item.type
        if item.type == "EC2 Instance":
            subgroup = (
                "GPU Workstations"
                if item.tags.get("Profile", "").lower().startswith("gpu")
                else "Control Workstations"
                if "control" in item.tags.get("Profile", "").lower()
                else "Other Instances"
            )
        grouped[GROUPS.get(item.type, "Other")][subgroup].append(item)
    return {group: dict(types) for group, types in grouped.items()}
