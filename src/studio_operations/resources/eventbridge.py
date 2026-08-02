from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("events", region_name=region)
    found = []
    for page in pages(client, "list_rules"):
        for item in page.get("Rules", []):
            tags = client.list_tags_for_resource(ResourceARN=item["Arn"]).get("Tags", [])
            found.append(
                resource(
                    item["Arn"],
                    "EventBridge Rule",
                    region,
                    tags,
                    state=item.get("State", "unknown"),
                    metadata={"rule_name": item["Name"]},
                )
            )
    return found
