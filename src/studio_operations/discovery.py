from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from importlib import import_module
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from studio_operations.models import Resource
from studio_operations.resources import (
    cloudwatch,
    codebuild,
    ebs,
    ec2,
    efs,
    eventbridge,
    iam,
    key_pairs,
    s3,
    security_groups,
)

lambda_resource = import_module("studio_operations.resources.lambda")

LOG = logging.getLogger(__name__)
Discoverer = Callable[[Any, str], list[Resource]]
DISCOVERERS: tuple[Discoverer, ...] = (
    ec2.discover,
    ebs.discover,
    efs.discover,
    s3.discover,
    iam.discover,
    security_groups.discover,
    key_pairs.discover,
    codebuild.discover,
    eventbridge.discover,
    cloudwatch.discover,
    lambda_resource.discover,
)


def enabled_regions(session: Any, requested: Sequence[str] | None = None) -> list[str]:
    if requested:
        return list(dict.fromkeys(requested))
    region = session.region_name or "us-east-1"
    try:
        response = session.client("ec2", region_name=region).describe_regions(AllRegions=False)
        return sorted(item["RegionName"] for item in response["Regions"])
    except (BotoCoreError, ClientError):
        LOG.warning("Unable to enumerate regions; using %s", region)
        return [region]


def discover_resources(
    session: Any,
    regions: Sequence[str] | None = None,
    discoverers: Sequence[Discoverer] = DISCOVERERS,
) -> list[Resource]:
    found: list[Resource] = []
    global_seen: set[Discoverer] = set()
    for region in enabled_regions(session, regions):
        for discoverer in discoverers:
            if discoverer in (iam.discover, s3.discover) and discoverer in global_seen:
                continue
            try:
                found.extend(discoverer(session, region))
                global_seen.add(discoverer)
            except (BotoCoreError, ClientError) as exc:
                LOG.warning("Discovery failed for %s in %s: %s", discoverer.__module__, region, exc)
    return found
