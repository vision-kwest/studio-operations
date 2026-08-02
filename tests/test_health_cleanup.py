from datetime import UTC, datetime, timedelta

from studio_operations.cleanup import plan_cleanup
from studio_operations.health import assess
from studio_operations.models import HealthStatus, Resource


def test_expired_resource_is_critical_and_cleanup_candidate():
    item = Resource(
        "i-1", "EC2 Instance", "us-east-1", expires=datetime.now(UTC) - timedelta(days=1)
    )
    assert assess(item).health is HealthStatus.CRITICAL
    assert plan_cleanup([item])[0].reason == "Expired deployment"


def test_detached_volume_warning_and_cleanup():
    item = Resource("vol-1", "EBS Volume", "us-east-1", metadata={"attachments": []})
    assert assess(item).health is HealthStatus.WARNING
    assert plan_cleanup([item])[0].action == "delete"
