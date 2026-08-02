from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("ec2", region_name=region)
    found = []
    for page in pages(client, "describe_key_pairs"):
        for item in page.get("KeyPairs", []):
            found.append(
                resource(
                    item.get("KeyPairId", item["KeyName"]),
                    "Key Pair",
                    region,
                    item.get("Tags"),
                    state="available",
                    metadata={"key_name": item["KeyName"]},
                )
            )
    return found
