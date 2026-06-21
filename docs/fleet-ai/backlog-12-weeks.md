# FleetPilot — Technical Backlog (12 недель)

**Проект:** FleetPilot MVP  
**Спринты:** 6 × 2 недели  
**Velocity target:** 40–50 SP / sprint (команда 2–3 dev)  
**Linear/Jira labels:** `mvp`, `p0`, `p1`, `p2`, `frontend`, `backend`, `ai`, `infra`, `design`, `integrations`

---

## Epic map

| Epic | ID | SP total | Weeks |
|------|-----|----------|-------|
| E1 Platform & Auth | EP-1 | 18 | 1–2 |
| E2 Integration Hub | EP-2 | 32 | 2–5 |
| E3 Fleet Map & Telemetry | EP-3 | 24 | 3–6 |
| E4 Fuel Agent | EP-4 | 22 | 4–7 |
| E5 Route Agent | EP-5 | 20 | 5–8 |
| E6 Dispatch Agent | EP-6 | 20 | 6–9 |
| E7 Maintenance Agent | EP-7 | 12 | 7–9 |
| E8 ROI & Analytics | EP-8 | 14 | 8–10 |
| E9 Billing & GTM | EP-9 | 14 | 10–12 |
| E10 Observability & Launch | EP-10 | 12 | 11–12 |
| **TOTAL** | | **~188 SP** | |

---

## Sprint 1 (Week 1–2) — Foundation

**Goal:** Repo, CI, auth, org + fleet model, dashboard shell.

| ID | Title | Type | SP | Priority | Labels |
|----|-------|------|-----|----------|--------|
| FP-1 | Monorepo setup: Next.js + FastAPI + Docker Compose | Task | 3 | P0 | infra |
| FP-2 | PostgreSQL schema v1: Organization, User, Vehicle, Integration | Task | 5 | P0 | backend |
| FP-3 | Auth: signup/login, JWT, org invite | Story | 5 | P0 | backend, frontend |
| FP-4 | RBAC: Admin, Dispatcher, FleetManager, Driver, Viewer | Story | 3 | P0 | backend |
| FP-5 | App shell: sidebar nav, ROI dashboard wireframe → UI | Story | 3 | P0 | frontend, design |
| FP-6 | CI: GitHub Actions lint + test + Docker build | Task | 2 | P0 | infra |
| FP-7 | Dev README + seed script (demo fleet 32 ТС) | Task | 1 | P1 | infra |
| FP-8 | Sentry + env config (.env.example) | Task | 2 | P1 | infra |

**Sprint 1 exit criteria:** User registers, creates org, sees empty fleet dashboard with KPI placeholders.

---

## Sprint 2 (Week 3–4) — Integration Hub

**Goal:** Omnicomm + СтавТРЭК adapters, vehicle mapping, sync jobs.

| ID | Title | Type | SP | Priority | Labels |
|----|-------|------|-----|----------|--------|
| FP-10 | Integration model: provider, credentials (encrypted), health | Task | 3 | P0 | backend |
| FP-11 | Omnicomm adapter: REST API, GPS + fuel polling | Story | 8 | P0 | integrations, backend |
| FP-12 | СтавТРЭК adapter: REST API, GPS sync | Story | 5 | P0 | integrations, backend |
| FP-13 | Unified Vehicle Model + external_ids mapping UI | Story | 5 | P0 | backend, frontend |
| FP-14 | Celery + Redis sync workers (30 sec interval) | Task | 3 | P0 | infra, backend |
| FP-15 | Integration Hub UI: connect, status, force sync | Story | 5 | P0 | frontend, design |
| FP-16 | Credentials vault: AES-256 at rest | Task | 3 | P0 | backend, infra |
| FP-17 | Integration health API + alert on sync failure | Story | 3 | P1 | backend |
| FP-18 | MSS GLONASS adapter (stub + docs) | Story | 3 | P1 | integrations |

**Sprint 2 exit criteria:** Omnicomm connected; 28+ vehicles synced; mapping table editable.

---

## Sprint 3 (Week 5–6) — Fleet Map & Telemetry

**Goal:** Real-time map, telemetry storage, alerts skeleton.

| ID | Title | Type | SP | Priority | Labels |
|----|-------|------|-----|----------|--------|
| FP-20 | TimescaleDB hypertable: vehicle_telemetry | Task | 3 | P0 | backend, infra |
| FP-21 | Fleet map API: SSE real-time positions | Story | 5 | P0 | backend |
| FP-22 | MapLibre map UI: markers, clusters, vehicle popup | Story | 8 | P0 | frontend, design |
| FP-23 | Vehicle list + filters (status, source, driver) | Story | 3 | P0 | frontend |
| FP-24 | Route deviation detection (geo-fence vs planned) | Story | 5 | P0 | backend, ai |
| FP-25 | Alert engine v1: types, severity, notify | Story | 5 | P0 | backend |
| FP-26 | Alerts inbox UI + acknowledge flow | Story | 3 | P0 | frontend, design |
| FP-27 | Driver working time report (GPS-based) | Story | 3 | P1 | backend |
| FP-28 | Offline vehicle detection + stale data badge | Task | 2 | P1 | backend |

**Sprint 3 exit criteria:** Live map with Omnicomm data; deviation alert fires on test route.

---

## Sprint 4 (Week 7–8) — Fuel Agent

**Goal:** Fuel dashboard, anomaly detection, driver scoring.

| ID | Title | Type | SP | Priority | Labels |
|----|-------|------|-----|----------|--------|
| FP-30 | Fuel baseline model per vehicle (l/100km) | Story | 5 | P0 | ai, backend |
| FP-31 | Anomaly detection: sudden drop, off-route refuel | Story | 8 | P0 | ai, backend |
| FP-32 | Confidence gating: ≥0.85 auto-alert, else review | Story | 3 | P0 | ai, backend |
| FP-33 | Fuel Agent dashboard UI | Story | 5 | P0 | frontend, design |
| FP-34 | Theft/drain events table + investigate workflow | Story | 3 | P0 | frontend, backend |
| FP-35 | Driver fuel rating leaderboard | Story | 3 | P0 | frontend |
| FP-36 | Monthly fuel savings report (PDF export) | Story | 3 | P1 | backend |
| FP-37 | Langfuse tracing for Fuel Agent decisions | Task | 2 | P1 | ai, infra |

**Sprint 4 exit criteria:** Simulated drain event → alert in <2 min; monthly savings report generated.

---

## Sprint 5 (Week 9–10) — Route Agent

**Goal:** Route optimization, human approval, TMS push.

| ID | Title | Type | SP | Priority | Labels |
|----|-------|------|-----|----------|--------|
| FP-40 | Yandex Maps Routing API integration | Story | 5 | P0 | integrations, backend |
| FP-41 | OR-Tools VRP solver: multi-stop routes | Story | 8 | P0 | ai, backend |
| FP-42 | Route comparison UI: manual vs optimized | Story | 5 | P0 | frontend, design |
| FP-43 | Human approval flow → push to driver/TMS | Story | 3 | P0 | backend, frontend |
| FP-44 | LLM route explanation (why this route) | Story | 3 | P1 | ai, backend |
| FP-45 | Constraints: time windows, capacity, ADR | Story | 5 | P1 | backend |
| FP-46 | Route history + savings audit log | Story | 3 | P0 | backend |
| FP-47 | Weather/traffic factor hook (Yandex traffic) | Story | 3 | P1 | backend |

**Sprint 5 exit criteria:** 5-stop route optimized; savings % shown; dispatcher approves in UI.

---

## Sprint 6 (Week 11–12) — Dispatch, Maintenance, Billing, Launch

**Goal:** Dispatch Agent, Maintenance Agent, ROI dashboard, production launch.

| ID | Title | Type | SP | Priority | Labels |
|----|-------|------|-----|----------|--------|
| FP-50 | Dispatch Agent: order parse (email/Excel/API) | Story | 8 | P0 | ai, backend |
| FP-51 | Dispatch: classify FTL/LTL + top-3 assignment | Story | 5 | P0 | ai, backend |
| FP-52 | Dispatch UI: proposals + approve/reject | Story | 5 | P0 | frontend, design |
| FP-53 | Maintenance Agent: interval rules + CAN DTC | Story | 5 | P0 | ai, backend |
| FP-54 | Maintenance schedule UI + 14-day forecast | Story | 3 | P0 | frontend |
| FP-55 | ROI dashboard: savings by agent, NPV calc | Story | 5 | P0 | backend, frontend |
| FP-56 | Master TMS adapter (bidirectional orders) | Story | 5 | P1 | integrations |
| FP-57 | ЮKassa checkout + usage metering (vehicles/plan) | Story | 5 | P0 | backend |
| FP-58 | Billing UI: plan, usage, upgrade | Story | 3 | P1 | frontend |
| FP-59 | Onboarding wizard: profile → connect GPS → map vehicles | Story | 3 | P1 | frontend, design |
| FP-60 | E2E tests: connect Omnicomm → fuel alert → ROI | Task | 5 | P0 | infra |
| FP-61 | Production deploy Yandex Cloud + runbook | Task | 5 | P0 | infra |
| FP-62 | Founding customer admin: manual plan override | Task | 2 | P1 | backend |
| FP-63 | Rate limiting + LLM cost cap per org | Task | 3 | P0 | backend, infra |
| FP-64 | Security review: RLS, credentials, 152-ФЗ checklist | Task | 3 | P0 | infra |
| FP-65 | Landing + pitch-deck on Vercel (GTM) | Task | 2 | P1 | infra |

**Sprint 6 exit criteria:** Production live; 1+ pilot customer; full agent pipeline demo; billing works.

---

## Backlog (post-MVP, P2)

| ID | Title | SP | Notes |
|----|-------|-----|-------|
| FP-70 | ANTOR TMS adapter | 5 | |
| FP-71 | AXELOT WMS connector | 8 | Этап 3 |
| FP-72 | ЯРД 2.0 YMS integration | 5 | |
| FP-73 | ЭТрН / Diadoc integration | 8 | |
| FP-74 | «Умная логистика» ERP sync | 8 | |
| FP-75 | Driver mobile app (React Native) | 13 | |
| FP-76 | On-prem Helm chart | 13 | Enterprise |
| FP-77 | 1С ТО integration | 5 | |

---

## Dependency graph (critical path)

```
FP-1 → FP-2 → FP-3 → FP-11 → FP-21 → FP-22
                ↓         ↓
              FP-10    FP-30 → FP-31 → FP-55
                ↓
              FP-40 → FP-41 → FP-43
                ↓
              FP-50 → FP-52 → FP-57
```

---

## Definition of Done (all tickets)

- [ ] Code reviewed + merged to `main`
- [ ] Unit tests for business logic
- [ ] API documented in OpenAPI (if backend)
- [ ] Langfuse trace for AI tickets
- [ ] No P0 linter errors
- [ ] Deployed to staging and smoke-tested

---

## Linear / Jira import

| Файл | Назначение |
|------|------------|
| [`backlog-linear-import.csv`](backlog-linear-import.csv) | Linear → Settings → Import → CSV |
| [`backlog-jira-import.csv`](backlog-jira-import.csv) | Jira Cloud External Import |

---

## Sprint calendar

| Sprint | Dates (example) | Demo |
|--------|-----------------|------|
| S1 | Jul 1 – Jul 14 | Auth + fleet dashboard shell |
| S2 | Jul 15 – Jul 28 | Omnicomm connected, vehicle sync |
| S3 | Jul 29 – Aug 11 | Live map + deviation alerts |
| S4 | Aug 12 – Aug 25 | Fuel Agent + drain detection |
| S5 | Aug 26 – Sep 8 | Route optimization + approval |
| S6 | Sep 9 – Sep 22 | Dispatch + billing + launch |

---

*Version 1.0 · 21.06.2026*
