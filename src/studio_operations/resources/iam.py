from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("iam")
    found = []
    for page in pages(client, "list_roles"):
        for item in page.get("Roles", []):
            tags = client.list_role_tags(RoleName=item["RoleName"]).get("Tags", [])
            found.append(
                resource(
                    item["Arn"],
                    "IAM Role",
                    "global",
                    tags,
                    state="available",
                    created=item.get("CreateDate"),
                    metadata={"role_name": item["RoleName"]},
                )
            )
    return found
