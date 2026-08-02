from datetime import UTC

from studio_operations.tags import missing_standard_tags, normalize_tags, parse_time


def test_normalizes_aws_tags_and_time():
    tags = normalize_tags([{"Key": "Owner", "Value": "artist"}, {"Key": "Empty"}])
    assert tags == {"Owner": "artist", "Empty": ""}
    assert parse_time("2026-01-02T03:04:05Z").tzinfo == UTC
    assert "Project" in missing_standard_tags(tags)
