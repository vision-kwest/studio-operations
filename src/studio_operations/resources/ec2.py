from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("ec2", region_name=region)
    found = []
    for page in pages(client, "describe_instances"):
        for reservation in page.get("Reservations", []):
            for item in reservation.get("Instances", []):
                found.append(
                    resource(
                        item["InstanceId"],
                        "EC2 Instance",
                        region,
                        item.get("Tags"),
                        state=item.get("State", {}).get("Name", "unknown"),
                        created=item.get("LaunchTime"),
                        metadata={
                            "instance_type": item.get("InstanceType"),
                            "role": item.get("IamInstanceProfile"),
                        },
                    )
                )
    return found
