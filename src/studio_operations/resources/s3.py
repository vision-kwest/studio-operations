from typing import Any

from botocore.exceptions import ClientError

from studio_operations.models import ChargeCategory, Resource

from .base import resource


def discover(session: Any, region: str) -> list[Resource]:
    client = session.client("s3", region_name=region)
    found = []
    for item in client.list_buckets().get("Buckets", []):
        try:
            tags = client.get_bucket_tagging(Bucket=item["Name"]).get("TagSet", [])
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "NoSuchTagSet":
                tags = []
            else:
                raise
        value = resource(
            item["Name"],
            "S3 Bucket",
            region,
            tags,
            state="available",
            created=item.get("CreationDate"),
        )
        value.cost.category = ChargeCategory.STORAGE
        found.append(value)
    return found
