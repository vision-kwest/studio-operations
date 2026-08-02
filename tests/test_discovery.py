from studio_operations.discovery import discover_resources
from studio_operations.models import Resource


class Session:
    region_name = "us-east-1"


def test_discovery_composes_adapters_without_aws():
    calls = []

    def adapter(session, region):
        calls.append(region)
        return [Resource("x", "Test", region)]

    result = discover_resources(Session(), ["eu-west-1"], [adapter])
    assert result[0].region == "eu-west-1"
    assert calls == ["eu-west-1"]
