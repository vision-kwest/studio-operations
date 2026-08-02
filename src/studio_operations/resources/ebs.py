from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import ChargeCategory, Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("ec2", region_name=region)
    found = []
    for page in pages(client, "describe_volumes"):
        for item in page.get("Volumes", []):
            value = resource(
                item["VolumeId"],
                "EBS Volume",
                region,
                item.get("Tags"),
                state=item.get("State", "unknown"),
                created=item.get("CreateTime"),
                metadata={"size_gib": item.get("Size"), "attachments": item.get("Attachments", [])},
            )
            value.cost.category = ChargeCategory.STORAGE
            found.append(value)
    return found
