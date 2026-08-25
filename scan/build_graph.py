#!/usr/bin/env python3
"""Build an interactive architecture graph for FleetPilot (Foglamp Scan style)."""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "data" / "graph.json"

SKIP_DIRS = {
    ".git",
    ".next",
    "node_modules",
    ".venv",
    "__pycache__",
    "dist",
    "out",
    "ui",
    "graphify-out",
    "canvases",
    ".cursor",
}

PY_EXT = {".py"}
TS_EXT = {".ts", ".tsx"}


@dataclass
class Node:
    id: str
    label: str
    kind: str
    layer: str
    path: str = ""
    summary: str = ""
    metrics: dict = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    target: str
    kind: str = "depends"


def rel(p: Path) -> str:
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def walk_files(base: Path, extensions: set[str]) -> list[Path]:
    out: list[Path] = []
    if not base.exists():
        return out
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix not in extensions:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def py_imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return set()
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
    return mods


def ts_imports(text: str) -> set[str]:
    mods: set[str] = set()
    for m in re.finditer(r"""from\s+['"]([^'"]+)['"]""", text):
        mods.add(m.group(1))
    for m in re.finditer(r"""import\s+['"]([^'"]+)['"]""", text):
        mods.add(m.group(1))
    return mods


def kind_for_path(path: str) -> tuple[str, str]:
    p = path.replace("\\", "/")
    if p.startswith("apps/web/src/app/"):
        return "page", "client"
    if p.startswith("apps/web/src/components/"):
        return "component", "client"
    if p.startswith("apps/web/src/lib/"):
        return "lib", "client"
    if p.startswith("apps/api/app/api/"):
        return "route", "api"
    if p.startswith("apps/api/app/services/"):
        return "service", "api"
    if p.startswith("apps/api/app/models/"):
        return "model", "store"
    if p.startswith("apps/api/app/schemas/"):
        return "schema", "api"
    if p.startswith("apps/api/app/core/"):
        return "core", "api"
    if p.startswith("apps/api/app/integrations/"):
        return "integration", "external"
    if p.startswith("apps/api/alembic/"):
        return "migration", "store"
    if p.startswith("agents/"):
        return "agent", "agent"
    if p.startswith("apps/desktop/"):
        return "desktop", "client"
    if p.startswith("landing/"):
        return "landing", "client"
    if p.startswith(".github/workflows/"):
        return "ci", "infra"
    if p.startswith("scripts/"):
        return "script", "infra"
    if p.startswith("docs/"):
        return "doc", "infra"
    return "file", "other"


def slug(*parts: str) -> str:
    return ":".join(parts)


def add_node(nodes: dict[str, Node], node: Node) -> None:
    nodes[node.id] = node


def build() -> dict:
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []
    edge_keys: set[tuple[str, str, str]] = set()

    def link(src: str, tgt: str, kind: str = "depends") -> None:
        if src == tgt or src not in nodes or tgt not in nodes:
            return
        key = (src, tgt, kind)
        if key in edge_keys:
            return
        edge_keys.add(key)
        edges.append(Edge(src, tgt, kind))

    # --- Top-level apps ---
    apps = [
        ("app:web", "Next.js Web", "client", "Web UI · dashboard, fleet ops"),
        ("app:desktop", "Electron Desktop", "client", "Windows shell · static Next export"),
        ("app:landing", "Marketing Landing", "client", "Vercel · CTA + installer download"),
        ("app:api", "FastAPI API", "api", "Core backend · :8800"),
    ]
    for nid, label, kind, summary in apps:
        add_node(nodes, Node(nid, label, kind, "apps", summary=summary))

    # --- Stores & infra ---
    stores = [
        ("store:postgres", "PostgreSQL", "store", "Tenant data · Alembic migrations"),
        ("store:redis", "Redis", "store", "Invite tokens · rate limits"),
    ]
    for nid, label, kind, summary in stores:
        add_node(nodes, Node(nid, label, kind, "stores", summary=summary))

    infra = [
        ("infra:docker", "Docker Compose", "infra", "postgres + redis + api"),
        ("infra:ci", "GitHub Actions", "infra", "app-ci · preview · deploy"),
    ]
    for nid, label, kind, summary in infra:
        add_node(nodes, Node(nid, label, kind, "infra", summary=summary))

    link("app:api", "store:postgres", "persists")
    link("app:api", "store:redis", "cache")
    link("infra:docker", "app:api", "runs")
    link("infra:docker", "store:postgres", "runs")
    link("infra:docker", "store:redis", "runs")
    link("app:web", "app:api", "http")
    link("app:desktop", "app:api", "http")
    link("app:landing", "app:desktop", "download")

    # --- API route groups (from router) ---
    route_groups = [
        ("route:health", "Health / Meta", "health.py · readiness"),
        ("route:auth", "Auth", "signup · login · JWT · invite"),
        ("route:analytics", "Analytics ROI", "KPI dashboard data"),
        ("route:fleet", "Fleet Ops", "vehicles · fuel · orders · integrations"),
        ("route:ops", "Ops UI", "routes · maintenance · settings"),
        ("route:permit", "Permit Agent API", "AI permit analysis"),
        ("route:rosdor", "Rosdor Integration", "registry check · sync"),
    ]
    for nid, label, summary in route_groups:
        add_node(nodes, Node(nid, label, "route", "api", summary=summary))
        link("app:api", nid, "routes")

    # --- External integrations ---
    externals = [
        ("ext:wialon", "Wialon Local", "GPS telematics DEMO"),
        ("ext:transmanager", "TransManager", "TMS orders DEMO"),
        ("ext:rosdor", "Rosdor Monitoring", "Permit registry"),
        ("ext:rosdor_parser", "Parser API", "External permit lookup"),
    ]
    for nid, label, summary in externals:
        add_node(nodes, Node(nid, label, "external", "external", summary=summary))
    link("route:fleet", "ext:wialon", "integrates")
    link("route:fleet", "ext:transmanager", "integrates")
    link("route:rosdor", "ext:rosdor", "integrates")
    link("route:rosdor", "ext:rosdor_parser", "integrates")

    # --- Agent templates ---
    agent_dirs = sorted((ROOT / "agents").glob("*-agent"))
    for agent_path in agent_dirs:
        name = agent_path.name.replace("-agent", "")
        nid = f"agent:{name}"
        add_node(
            nodes,
            Node(
                nid,
                f"{name.title()} Agent",
                "agent",
                "agents",
                path=rel(agent_path),
                summary=f"LLM template · {agent_path.name}",
            ),
        )
        link(nid, "app:api", "calls")
        if name == "permit":
            link("route:permit", nid, "exposes")
        if name == "route":
            link("route:ops", nid, "related")
        if name == "fuel":
            link("route:fleet", nid, "related")
        if name == "dispatch":
            link("route:fleet", nid, "related")
        if name == "maintenance":
            link("route:ops", nid, "related")

    add_node(
        nodes,
        Node("agent:shared", "Shared Agent Lib", "agent", "agents", summary="event_bus · alerting · vehicle_model"),
    )
    for agent_path in agent_dirs:
        link(f"agent:{agent_path.name.replace('-agent', '')}", "agent:shared", "uses")

    # --- Web pages (from sidebar + auth) ---
    pages = [
        ("/login", "Login"),
        ("/signup", "Signup"),
        ("/dashboard", "ROI Dashboard"),
        ("/dispatch", "Dispatch"),
        ("/map", "Fleet Map"),
        ("/routes", "Routes"),
        ("/fuel", "Fuel Alerts"),
        ("/maintenance", "Maintenance"),
        ("/integrations", "Integrations"),
        ("/settings", "Settings"),
        ("/pilot", "Permits Pilot"),
    ]
    for href, label in pages:
        pid = f"page:{href.strip('/') or 'home'}"
        add_node(nodes, Node(pid, label, "page", "client", path=f"apps/web/src/app{href}/page.tsx", summary=href))
        link("app:web", pid, "renders")

    page_api_map = {
        "login": "route:auth",
        "signup": "route:auth",
        "dashboard": "route:analytics",
        "dispatch": "route:fleet",
        "map": "route:fleet",
        "routes": "route:ops",
        "fuel": "route:fleet",
        "maintenance": "route:ops",
        "integrations": "route:fleet",
        "settings": "route:ops",
        "pilot": "route:permit",
    }
    for page, route in page_api_map.items():
        link(f"page:{page}", route, "fetch")

    # --- File-level nodes (sampled clusters) ---
    file_to_node: dict[str, str] = {}

    def register_file(path: Path) -> str:
        r = rel(path)
        if r in file_to_node:
            return file_to_node[r]
        subkind, layer = kind_for_path(r)
        stem = path.stem
        if stem in ("__init__", "page", "layout"):
            stem = path.parent.name
        nid = slug("file", layer, r.replace("/", "_").replace(".", "_")[:80])
        if nid in nodes:
            return nid
        label = stem if len(stem) < 24 else stem[:21] + "…"
        add_node(
            nodes,
            Node(nid, label, subkind, layer, path=r, summary=r),
        )
        file_to_node[r] = nid
        return nid

    py_files = walk_files(ROOT / "apps" / "api", PY_EXT)
    ts_files = walk_files(ROOT / "apps" / "web" / "src", TS_EXT)

    service_nodes: dict[str, str] = {}
    model_nodes: dict[str, str] = {}

    for pf in py_files:
        r = rel(pf)
        if "/app/services/" in r and pf.stem != "__init__":
            nid = slug("service", pf.stem)
            service_nodes[pf.stem] = nid
            add_node(nodes, Node(nid, pf.stem.replace("_", " ").title(), "service", "api", path=r))
            link("app:api", nid, "implements")
            if pf.stem == "auth_service":
                link("route:auth", nid, "uses")
            elif pf.stem == "fleet_service":
                link("route:fleet", nid, "uses")
            elif pf.stem == "ops_service":
                link("route:ops", nid, "uses")
            elif pf.stem == "analytics_service":
                link("route:analytics", nid, "uses")
            elif pf.stem == "permit_service":
                link("route:permit", nid, "uses")
        elif "/app/models/" in r and pf.stem != "__init__":
            nid = slug("model", pf.stem)
            model_nodes[pf.stem] = nid
            add_node(nodes, Node(nid, pf.stem.replace("_", " ").title(), "model", "store", path=r))
            link("store:postgres", nid, "tables")

    for pf in py_files:
        r = rel(pf)
        if "/app/services/" not in r:
            continue
        svc = pf.stem
        if svc == "__init__" or svc not in service_nodes:
            continue
        text = pf.read_text(encoding="utf-8", errors="ignore")
        for model in model_nodes:
            if model in text:
                link(service_nodes[svc], model_nodes[model], "queries")

    lib_nodes: dict[str, str] = {}
    for tf in ts_files:
        r = rel(tf)
        if "/lib/" in r:
            nid = slug("lib", tf.stem)
            lib_nodes[tf.stem] = nid
            add_node(nodes, Node(nid, tf.stem, "lib", "client", path=r))
            link("app:web", nid, "shared")

    for tf in ts_files:
        r = rel(tf)
        if "/app/" not in r or not r.endswith("page.tsx"):
            continue
        page_key = Path(r).parent.name
        pid = f"page:{page_key}"
        if pid not in nodes:
            continue
        text = tf.read_text(encoding="utf-8", errors="ignore")
        for imp in ts_imports(text):
            if imp.startswith("@/lib/"):
                lib_name = imp.split("/")[-1]
                if lib_name in lib_nodes:
                    link(pid, lib_nodes[lib_name], "imports")

    # --- Metrics & personality ---
    counts = Counter(n.kind for n in nodes.values())
    loc_py = sum(len(f.read_text(encoding="utf-8", errors="ignore").splitlines()) for f in py_files)
    loc_ts = sum(len(f.read_text(encoding="utf-8", errors="ignore").splitlines()) for f in ts_files)

    traits = {
        "fleet_ops": counts.get("service", 0) + counts.get("page", 0),
        "multi_tenant": 1 if "model:organization" in nodes or any("organization" in n.id for n in nodes.values()) else 0,
        "agent_ready": counts.get("agent", 0),
        "integration_heavy": counts.get("external", 0),
        "ui_surface": counts.get("page", 0) + counts.get("component", 0),
        "api_depth": counts.get("route", 0) + counts.get("service", 0),
    }
    dominant = max(traits, key=traits.get)

    personalities = {
        "fleet_ops": ("Fleet Operator", "Ops-first B2B SaaS for transport companies"),
        "agent_ready": ("Agent Orchestrator", "AI agent templates wired to API endpoints"),
        "integration_heavy": ("Integration Hub", "Connectors to telematics, TMS, and registries"),
        "ui_surface": ("Dashboard Product", "Rich operator UI across fleet workflows"),
        "api_depth": ("API Backbone", "Service-layer driven backend architecture"),
        "multi_tenant": ("Tenant Platform", "Organization-scoped multi-tenant data model"),
    }
    title, tagline = personalities.get(dominant, ("FleetPilot", "Transport logistics platform"))

    stats = {
        "files_python": len(py_files),
        "files_typescript": len(ts_files),
        "loc_python": loc_py,
        "loc_typescript": loc_ts,
        "nodes": len(nodes),
        "edges": len(edges),
    }

    kind_groups = {
        "Clients": ["client", "page", "component", "lib", "desktop", "landing"],
        "API": ["api", "route", "service", "schema", "core"],
        "Stores": ["store", "model", "migration"],
        "Agents": ["agent"],
        "External": ["external", "integration"],
        "Infra": ["infra", "ci", "script", "doc"],
    }

    return {
        "meta": {
            "project": "FleetPilot",
            "repo": ROOT.name,
            "generated_at": datetime.now(UTC).isoformat(),
            "scanner": "fleetpilot-scan/1.0",
        },
        "personality": {
            "title": title,
            "tagline": tagline,
            "dominant_trait": dominant,
            "traits": traits,
        },
        "stats": stats,
        "kind_groups": kind_groups,
        "nodes": [
            {
                "id": n.id,
                "label": n.label,
                "kind": n.kind,
                "layer": n.layer,
                "path": n.path,
                "summary": n.summary,
                "metrics": n.metrics,
            }
            for n in nodes.values()
        ],
        "edges": [{"source": e.source, "target": e.target, "kind": e.kind} for e in edges],
    }


def main() -> int:
    graph = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} — {graph['stats']['nodes']} nodes, {graph['stats']['edges']} edges")
    print(f"Personality: {graph['personality']['title']} — {graph['personality']['tagline']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
