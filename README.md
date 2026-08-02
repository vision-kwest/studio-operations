# studio-operations

`studio-operations` is the **Operations Plane** for the Studio Platform. It inventories,
audits, monitors, reports on, and creates safe cleanup plans for resources already present in
AWS. It never provisions infrastructure, installs software, executes OpenTofu, or reads an
OpenTofu state file. AWS is the source of truth.

## Architecture

```text
launch-control-workstation → Control Workstation → studio-infrastructure
                                                    ↓
                                              GPU Workstations
                                                    ↓
                                             studio-operations
```

The CLI uses `boto3` and native AWS APIs. Small resource adapters independently discover EC2,
EBS, EFS, S3, IAM, security groups, key pairs, CodeBuild, EventBridge, CloudWatch Logs, and
Lambda resources. This keeps new resource support isolated and testable.

## Install and use

Python 3.12 or newer and normal AWS SDK credentials are required.

```bash
python -m pip install .
studio --profile studio --region us-east-1 inventory
studio inventory --json
studio health --json
studio costs --json
studio cleanup --dry-run
studio report --format markdown
studio doctor
```

Without `--region`, inventory scans enabled AWS regions. `--region` can be repeated. Discovery
continues when an individual API is unavailable and emits a structured warning to stderr.

## Inventory and reports

`studio inventory` is the primary single pane of glass. It groups compute, storage, networking,
IAM, monitoring, and automation resources and displays identity, ownership, deployment,
repository, environment, timestamps, state, health, and tags. `studio report` emits human,
JSON, or Markdown output; the internal serializable model allows future HTML rendering.

## Health

Health rules classify resources as **Healthy**, **Warning**, or **Critical**. Initial checks cover
stopped workstations, missing control-workstation IAM profiles, expired deployments, detached
EBS volumes, and EFS file systems without mount targets. The rules are deterministic and do not
modify AWS.

## Costs

`studio costs` uses AWS Cost Explorer to provide current-month and projected totals, daily
spend, and allocation by `Project`, `DeploymentID`, and `Owner`. Cost Explorer access and
cost-allocation tag activation remain AWS account responsibilities.

## Cleanup safety

`studio cleanup` only generates recommendations for expired deployments and apparently idle or
orphaned resources. `--dry-run` is non-interactive. Without it the CLI asks `Delete? [y/N]`, but
this release intentionally has no deletion executor: even affirmative input cannot modify AWS.

## Tagging contract

Tags are the operations-plane data model. Producers should apply all of these tags:

| Tag | Meaning |
| --- | --- |
| `Project` | Studio project or production |
| `Repository` | Creating repository |
| `DeploymentID` | Unique deployment identity |
| `Environment` | Environment such as dev or production |
| `Owner` | Responsible person or team |
| `ManagedBy` | Managing system |
| `Version` | Producer version |
| `Profile` | Workload profile, such as `gpu` or `control` |
| `CreationTime` | ISO-8601 creation time |
| `ExpirationTime` | ISO-8601 expiration time |

## AWS inventory services

The doctor checks authentication and access to **AWS Resource Explorer**, **AWS Resource
Groups**, and **AWS Cost Explorer**. Resource Explorer supplies an account-wide native search
surface, while Resource Groups can provide project, deployment, and owner views from the same
tag contract. Resource-specific APIs remain authoritative for operational state and metadata.

The CLI needs read-only permissions for the listed services, `sts:GetCallerIdentity`,
Resource Explorer search/index APIs, Resource Groups listing APIs, and Cost Explorer
`GetCostAndUsage`. `studio doctor` performs only read operations and reports missing services or
permissions.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src
```
