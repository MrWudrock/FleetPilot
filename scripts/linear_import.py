#!/usr/bin/env python3
"""
Import FleetPilot backlog into Linear via GraphQL API.

Usage:
  set LINEAR_API_KEY=lin_api_xxxxxxxx
  set LINEAR_TEAM_ID=optional-team-uuid
  python scripts/linear_import.py

  python scripts/linear_import.py --dry-run
  python scripts/linear_import.py --csv docs/fleet-ai/backlog-linear-import.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.linear.app/graphql"

PRIORITY_MAP = {
    "urgent": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}

MILESTONE_NAMES = {
    "Sprint 1": "Sprint 1 — Foundation",
    "Sprint 2": "Sprint 2 — Integrations",
    "Sprint 3": "Sprint 3 — Fleet Map",
    "Sprint 4": "Sprint 4 — Fuel Agent",
    "Sprint 5": "Sprint 5 — Route Agent",
    "Sprint 6": "Sprint 6 — Launch",
}


def load_local_env() -> None:
    """Load LINEAR_API_KEY from .linear.env or docs/fleet-ai/linear.env."""
    root = Path(__file__).resolve().parents[1]
    candidates = [
        root / ".linear.env",
        root / "linear.env",
        root / "docs" / "fleet-ai" / "linear.env",
    ]
    for env_file in candidates:
        if not env_file.exists():
            continue
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("api key "):
                os.environ.setdefault("LINEAR_API_KEY", line.split(None, 2)[-1].strip())
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value
        return


def count_project_issues(api_key: str, project_id: str) -> int:
    data = gql(
        api_key,
        """
        query ProjectIssues($id: String!) {
          project(id: $id) {
            issues { nodes { id } }
          }
        }
        """,
        {"id": project_id},
    )
    return len(data["project"]["issues"]["nodes"])


def gql(api_key: str, query: str, variables: dict | None = None) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {detail}") from e

    if body.get("errors"):
        raise RuntimeError(json.dumps(body["errors"], ensure_ascii=False, indent=2))
    return body["data"]


def list_teams(api_key: str) -> list[dict]:
    data = gql(
        api_key,
        """
        query Teams {
          teams {
            nodes { id key name }
          }
        }
        """,
    )
    return data["teams"]["nodes"]


def resolve_team_id(api_key: str, team_id: str | None) -> str:
    teams = list_teams(api_key)
    if not teams:
        raise RuntimeError("No teams found in Linear workspace")
    if team_id:
        for t in teams:
            if t["id"] == team_id or t["key"].lower() == team_id.lower():
                return t["id"]
        raise RuntimeError(f"Team not found: {team_id}")
    if len(teams) == 1:
        print(f"Using team: {teams[0]['name']} ({teams[0]['key']})")
        return teams[0]["id"]
    print("Available teams:")
    for t in teams:
        print(f"  - {t['key']}: {t['name']}  id={t['id']}")
    raise RuntimeError("Set LINEAR_TEAM_ID to one of the team ids/keys above")


def get_or_create_project(api_key: str, team_id: str, name: str, dry_run: bool) -> str:
    data = gql(
        api_key,
        """
        query Projects($name: String!) {
          projects(filter: { name: { eq: $name } }) {
            nodes { id name }
          }
        }
        """,
        {"name": name},
    )
    nodes = data["projects"]["nodes"]
    if nodes:
        print(f"Project exists: {name} ({nodes[0]['id']})")
        return nodes[0]["id"]

    if dry_run:
        print(f"[dry-run] Would create project: {name}")
        return "dry-run-project-id"

    created = gql(
        api_key,
        """
        mutation ProjectCreate($input: ProjectCreateInput!) {
          projectCreate(input: $input) {
            success
            project { id name url }
          }
        }
        """,
        {"input": {"name": name, "teamIds": [team_id]}},
    )
    project = created["projectCreate"]["project"]
    print(f"Created project: {project['name']} -> {project['url']}")
    return project["id"]


def get_project_milestones(api_key: str, project_id: str) -> dict[str, str]:
    data = gql(
        api_key,
        """
        query ProjectMilestones($id: String!) {
          project(id: $id) {
            projectMilestones { nodes { id name } }
          }
        }
        """,
        {"id": project_id},
    )
    return {n["name"]: n["id"] for n in data["project"]["projectMilestones"]["nodes"]}


def create_milestones(api_key: str, project_id: str, dry_run: bool) -> dict[str, str]:
    existing = {} if dry_run else get_project_milestones(api_key, project_id)
    result = dict(existing)

    for short, full in MILESTONE_NAMES.items():
        if full in result:
            continue
        if dry_run:
            print(f"[dry-run] Would create milestone: {full}")
            result[full] = f"dry-run-{short}"
            continue
        data = gql(
            api_key,
            """
            mutation MilestoneCreate($input: ProjectMilestoneCreateInput!) {
              projectMilestoneCreate(input: $input) {
                success
                projectMilestone { id name }
              }
            }
            """,
            {"input": {"projectId": project_id, "name": full}},
        )
        ms = data["projectMilestoneCreate"]["projectMilestone"]
        result[ms["name"]] = ms["id"]
        print(f"Created milestone: {ms['name']}")
        time.sleep(0.15)

    return result


def get_or_create_labels(api_key: str, team_id: str, names: list[str], dry_run: bool) -> dict[str, str]:
    data = gql(
        api_key,
        """
        query Labels {
          issueLabels {
            nodes { id name }
          }
        }
        """,
    )
    mapping = {n["name"]: n["id"] for n in data["issueLabels"]["nodes"]}
    for name in names:
        if name in mapping:
            continue
        if dry_run:
            mapping[name] = f"dry-run-{name}"
            continue
        created = gql(
            api_key,
            """
            mutation LabelCreate($input: IssueLabelCreateInput!) {
              issueLabelCreate(input: $input) {
                success
                issueLabel { id name }
              }
            }
            """,
            {"input": {"teamId": team_id, "name": name, "color": "#5e6ad2"}},
        )
        label = created["issueLabelCreate"]["issueLabel"]
        mapping[label["name"]] = label["id"]
        time.sleep(0.1)
    return mapping


def parse_csv(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def is_epic(row: dict) -> bool:
    labels = row.get("Labels", "")
    title = row.get("Title", "")
    return "epic" in labels.split(",") or title.strip().startswith("[EP-")


def create_issue(
    api_key: str,
    *,
    team_id: str,
    title: str,
    description: str,
    priority: int | None,
    estimate: int | None,
    label_names: list[str],
    label_ids: list[str],
    project_id: str | None,
    milestone_id: str | None,
    parent_id: str | None,
    dry_run: bool,
) -> str | None:
    if dry_run:
        prefix = "  [epic]" if not parent_id else "  "
        print(f"{prefix}[dry-run] {title} (est={estimate}, labels={','.join(label_names)})")
        return f"dry-run-{title[:20]}"

    input_data: dict = {
        "teamId": team_id,
        "title": title,
        "description": description or "",
    }
    if priority is not None:
        input_data["priority"] = priority
    if estimate:
        input_data["estimate"] = estimate
    if label_ids:
        input_data["labelIds"] = label_ids
    if project_id:
        input_data["projectId"] = project_id
    if milestone_id:
        input_data["projectMilestoneId"] = milestone_id
    if parent_id and not parent_id.startswith("dry-run"):
        input_data["parentId"] = parent_id

    data = gql(
        api_key,
        """
        mutation IssueCreate($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue { id identifier title url }
          }
        }
        """,
        {"input": input_data},
    )
    issue = data["issueCreate"]["issue"]
    print(f"  + {issue['identifier']} {issue['title']}")
    time.sleep(0.2)
    return issue["id"]


def import_backlog(api_key: str, csv_path: Path, team_id: str | None, dry_run: bool, force: bool = False) -> None:
    resolved_team = resolve_team_id(api_key, team_id)
    rows = parse_csv(csv_path)

    all_labels: set[str] = set()
    for row in rows:
        all_labels.update(x.strip() for x in row.get("Labels", "").split(",") if x.strip())
    label_map = get_or_create_labels(api_key, resolved_team, sorted(all_labels), dry_run)

    project_id = get_or_create_project(api_key, resolved_team, "FleetPilot", dry_run)
    if not dry_run and not project_id.startswith("dry-run") and not force:
        existing_count = count_project_issues(api_key, project_id)
        if existing_count >= 50:
            print(f"Project FleetPilot already has {existing_count} issues — skip import to avoid duplicates.")
            print("Delete issues in Linear or rename project, then re-run.")
            return

    milestones = create_milestones(api_key, project_id, dry_run)

    current_epic_id: str | None = None
    created = 0

    for row in rows:
        title = row["Title"].strip()
        description = row.get("Description", "").strip()
        priority = PRIORITY_MAP.get(row.get("Priority", "").strip().lower())
        estimate_raw = row.get("Estimate", "").strip()
        estimate = int(estimate_raw) if estimate_raw.isdigit() else None
        labels = [x.strip() for x in row.get("Labels", "").split(",") if x.strip()]
        label_ids = [label_map[l] for l in labels if l in label_map]
        milestone_key = row.get("Milestone", "").strip()
        milestone_name = MILESTONE_NAMES.get(milestone_key, milestone_key)
        milestone_id = milestones.get(milestone_name)

        if is_epic(row):
            print(f"Epic: {title}")
            current_epic_id = create_issue(
                api_key,
                team_id=resolved_team,
                title=title,
                description=description,
                priority=priority,
                estimate=estimate,
                label_names=labels,
                label_ids=label_ids,
                project_id=project_id,
                milestone_id=milestone_id,
                parent_id=None,
                dry_run=dry_run,
            )
            created += 1
            continue

        create_issue(
            api_key,
            team_id=resolved_team,
            title=title,
            description=description,
            priority=priority,
            estimate=estimate,
            label_names=labels,
            label_ids=label_ids,
            project_id=project_id,
            milestone_id=milestone_id,
            parent_id=current_epic_id,
            dry_run=dry_run,
        )
        created += 1

    print(f"\nDone. Processed {created} issues.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import FleetPilot backlog to Linear")
    parser.add_argument(
        "--csv",
        default=str(Path(__file__).resolve().parents[1] / "docs" / "fleet-ai" / "backlog-linear-import.csv"),
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without API writes")
    parser.add_argument("--force", action="store_true", help="Import even if project already has issues")
    args = parser.parse_args()

    load_local_env()
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key and not args.dry_run:
        print("Set LINEAR_API_KEY or create .linear.env (see .linear.env.example)", file=sys.stderr)
        print("Get key: Linear -> Settings -> Account -> API -> Personal API keys", file=sys.stderr)
        return 1

    team_id = os.environ.get("LINEAR_TEAM_ID", "").strip() or None
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("DRY RUN — no API key required for listing structure")
        if api_key:
            import_backlog(api_key, csv_path, team_id, dry_run=True)
        else:
            rows = parse_csv(csv_path)
            print(f"Would import {len(rows)} rows from {csv_path}")
        return 0

    import_backlog(api_key, csv_path, team_id, dry_run=False, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
