from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("ec2", region_name=region)
    found = []
    for page in pages(client, "describe_security_groups"):
        for item in page.get("SecurityGroups", []):
            found.append(
                resource(
                    item["GroupId"],
                    "Security Group",
                    region,
                    item.get("Tags"),
                    state="available",
                    metadata={
                        "group_name": item.get("GroupName"),
                        "vpc_id": item.get("VpcId"),
                        "rules": len(item.get("IpPermissions", []))
                        + len(item.get("IpPermissionsEgress", [])),
                    },
                )
            )
    return found
