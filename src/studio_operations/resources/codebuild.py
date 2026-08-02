from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("codebuild", region_name=region)
    names = []
    for page in pages(client, "list_projects"):
        names.extend(page.get("projects", []))
    found = []
    for offset in range(0, len(names), 100):
        for item in client.batch_get_projects(names=names[offset : offset + 100]).get(
            "projects", []
        ):
            found.append(
                resource(
                    item["arn"],
                    "CodeBuild Project",
                    region,
                    item.get("tags"),
                    state="available",
                    created=item.get("created"),
                    metadata={"project_name": item["name"]},
                )
            )
    return found
