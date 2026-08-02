from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import ChargeCategory, Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("efs", region_name=region)
    found = []
    for page in pages(client, "describe_file_systems"):
        for item in page.get("FileSystems", []):
            tags = client.describe_tags(FileSystemId=item["FileSystemId"]).get("Tags", [])
            value = resource(
                item["FileSystemId"],
                "EFS",
                region,
                tags,
                state=item.get("LifeCycleState", "unknown"),
                created=item.get("CreationTime"),
                metadata={
                    "size_bytes": item.get("SizeInBytes", {}).get("Value"),
                    "mount_targets": item.get("NumberOfMountTargets", 0),
                },
            )
            value.cost.category = ChargeCategory.STORAGE
            found.append(value)
    return found
