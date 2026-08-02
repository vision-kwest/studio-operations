from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

import boto3

from studio_operations.cleanup import plan_cleanup
from studio_operations.costs import get_costs
from studio_operations.discovery import discover_resources
from studio_operations.doctor import run_checks
from studio_operations.health import assess_all
from studio_operations.reports import inventory_data, render_inventory, render_json

LOG = logging.getLogger("studio")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="studio", description="Studio Platform AWS operations plane"
    )
    root.add_argument("--profile")
    root.add_argument("--region", action="append", dest="regions")
    root.add_argument("--verbose", action="store_true")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("inventory", "costs", "health", "report", "doctor"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--json", action="store_true")
        if name == "report":
            cmd.add_argument("--format", choices=("human", "json", "markdown"), default="human")
    cleanup = commands.add_parser("cleanup")
    cleanup.add_argument("--json", action="store_true")
    cleanup.add_argument("--dry-run", action="store_true")
    return root


def _write(value: str) -> None:
    sys.stdout.write(value)


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s %(message)s",
    )
    session = boto3.Session(
        profile_name=args.profile, region_name=args.regions[0] if args.regions else None
    )
    try:
        if args.command == "doctor":
            checks = run_checks(session)
            _write(
                render_json([x.to_dict() for x in checks])
                if args.json
                else "\n".join(
                    f"{'PASS' if x.ok else 'FAIL'}  {x.name}: {x.detail}" for x in checks
                )
                + "\n"
            )
            return 0 if all(x.ok for x in checks) else 1
        if args.command == "costs":
            costs = get_costs(session)
            _write(
                render_json(costs)
                if args.json
                else (
                    "Costs\n"
                    f"Current Month: ${costs.current_month:.2f}\n"
                    f"Estimated Monthly: ${costs.estimated_monthly:.2f}\n"
                    f"Per Project: {costs.by_project}\n"
                    f"Per Deployment: {costs.by_deployment}\n"
                    f"Per Owner: {costs.by_owner}\n"
                )
            )
            return 0
        resources = assess_all(discover_resources(session, args.regions))
        if args.command in ("inventory", "health", "report"):
            if args.command == "health":
                resources = [x for x in resources if x.health.value != "Healthy"]
            fmt = args.format if args.command == "report" else ("json" if args.json else "human")
            _write(
                render_json(inventory_data(resources))
                if fmt == "json"
                else render_inventory(resources, fmt == "markdown")
            )
            return 0
        actions = plan_cleanup(resources)
        if args.json:
            _write(render_json([x.to_dict() for x in actions]))
        else:
            _write(
                "Cleanup Recommendations\n"
                + "\n".join(f"- {x.resource_type} {x.resource_id}: {x.reason}" for x in actions)
                + "\n"
            )
            if actions and not args.dry_run:
                _write("Delete? [y/N] ")
                answer = sys.stdin.readline().strip().lower()
                _write(
                    "No resources deleted; cleanup execution is intentionally not implemented.\n"
                    if answer == "y"
                    else "Cancelled.\n"
                )
        return 0
    except (KeyboardInterrupt, EOFError):
        LOG.error("Cancelled")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
