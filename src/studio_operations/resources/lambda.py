from typing import Any

from studio_operations.common.aws import pages
from studio_operations.models import Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("lambda", region_name=region)
    found = []
    for page in pages(client, "list_functions"):
        for item in page.get("Functions", []):
            tags = client.list_tags(Resource=item["FunctionArn"]).get("Tags", {})
            found.append(
                resource(
                    item["FunctionArn"],
                    "Lambda Function",
                    region,
                    tags,
                    state=item.get("State", "active").lower(),
                    created=item.get("LastModified"),
                    metadata={
                        "function_name": item["FunctionName"],
                        "runtime": item.get("Runtime"),
                    },
                )
            )
    return found
