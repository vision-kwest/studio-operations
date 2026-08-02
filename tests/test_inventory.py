from studio_operations.inventory import group_resources
from studio_operations.models import Resource


def test_groups_gpu_workstation():
    item = Resource("i-1", "EC2 Instance", "us-east-1", tags={"Profile": "gpu-large"})
    assert group_resources([item])["Compute"]["GPU Workstations"] == [item]
