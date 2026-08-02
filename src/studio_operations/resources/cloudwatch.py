from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import ChargeCategory, Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("logs", region_name=region)
    found = []
    for page in pages(client, "describe_log_groups"):
        for item in page.get("logGroups", []):
            arn = item.get("arn", item["logGroupName"])
            tags = client.list_tags_for_resource(resourceArn=arn).get("tags", {})
            value = resource(
                arn,
                "CloudWatch Log Group",
                region,
                tags,
                state="available",
                metadata={
                    "log_group_name": item["logGroupName"],
                    "stored_bytes": item.get("storedBytes", 0),
                    "retention_days": item.get("retentionInDays"),
                },
            )
            value.cost.category = ChargeCategory.STORAGE
            found.append(value)
    return found
