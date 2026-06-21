# Архитектура FleetPilot

**Версия:** 1.0 · **Дата:** 21.06.2026

---

## 1. Обзор

FleetPilot — multi-tenant B2B SaaS с **Integration Hub** (коннекторы к российским TMS/GPS) и **Agent Orchestrator** (4 ИИ-агента). Архитектура наследует паттерны TenderPilot: human-in-the-loop, audit trail, данные в РФ.

---

## 2. High-level architecture

```mermaid
flowchart TB
    subgraph Client["Клиент"]
        WEB[Web App<br/>Next.js]
        MOB[Driver App<br/>post-MVP]
    end

    subgraph Edge["Edge"]
        CDN[CDN / WAF]
        GW[API Gateway]
    end

    subgraph App["Application"]
        API[Core API<br/>FastAPI]
        AUTH[Auth<br/>Supabase / Keycloak]
        HUB[Integration Hub]
        WF[Workflow<br/>Celery]
    end

    subgraph Agents["AI Agents"]
        ORCH[Agent Orchestrator<br/>LangGraph]
        ROUTE[Route Agent]
        DISP[Dispatch Agent]
        FUEL[Fuel Agent]
        MAINT[Maintenance Agent]
        LLM[LLM Router]
        RULES[Rules Engine]
    end

    subgraph Connectors["Russian Integrations"]
        OMNI[Omnicomm]
        STAV[СтавТРЭК]
        MSS[MSS GLONASS]
        TMS[Master TMS / ANTOR]
        MAPS[Yandex Maps]
    end

    subgraph Data["Data"]
        PG[(PostgreSQL<br/>+ TimescaleDB)]
        REDIS[(Redis)]
        S3[(Object Storage)]
        TS[(Time-series<br/>GPS/Fuel)]
    end

    WEB --> CDN --> GW --> API
    API --> AUTH
    API --> HUB
    API --> WF
    HUB --> OMNI & STAV & MSS & TMS
    WF --> ORCH
    ORCH --> ROUTE & DISP & FUEL & MAINT
    ROUTE --> MAPS
    ORCH --> LLM & RULES
    API --> PG & REDIS & S3
    HUB --> TS
```

---

## 3. Integration Hub (ключевой модуль)

```mermaid
flowchart LR
    subgraph Adapters
        A1[OmnicommAdapter]
        A2[StavTrackAdapter]
        A3[MssGlonassAdapter]
        A4[MasterTmsAdapter]
    end

    subgraph Normalization
        NORM[Unified Vehicle Model]
        EVT[Event Bus]
    end

    subgraph Consumers
        MAP[Fleet Map]
        FA[Fuel Agent]
        RA[Route Agent]
        DA[Dispatch Agent]
    end

    OMNI_API[Omnicomm API] --> A1
    STAV_API[СтавТРЭК API] --> A2
    MSS_API[MSS API] --> A3
    TMS_API[Master TMS] --> A4

    A1 & A2 & A3 & A4 --> NORM --> EVT
    EVT --> MAP & FA & RA & DA
```

**Unified Vehicle Model:**

```python
class VehicleState:
    vehicle_id: str          # FleetPilot internal
    external_ids: dict       # {"omnicomm": "123", "stavtrack": "456"}
    plate: str               # А123БВ777
    lat: float
    lon: float
    speed: float
    fuel_level: float | None
    fuel_rate: float | None
    driver_id: str | None
    status: enum             # moving | idle | offline
    last_update: datetime
```

**Adapter pattern:** каждый коннектор — отдельный Python-модуль с retry, rate limiting, health check.

---

## 4. Agent pipelines

### 4.1 Route Agent

```mermaid
sequenceDiagram
    participant D as Диспетчер
    participant API as Core API
    participant RA as Route Agent
    participant MAPS as Yandex Maps
    participant HUB as Integration Hub

    D->>API: Create route request (orders[], constraints)
    API->>RA: optimize_route
    RA->>HUB: Get vehicle positions
    RA->>MAPS: Matrix API + traffic
    RA->>RA: OR-Tools VRP solver
    RA->>RA: LLM explain deviations
    RA-->>D: Proposed routes + savings estimate
    D->>API: Approve route
    API->>HUB: Push to TMS / notify driver
```

### 4.2 Dispatch Agent

```
Input: заявка (email/Excel/API)
  → Parse & extract (LLM structured)
  → Classify (FTL/LTL, urgency, cargo type)
  → Match vehicles (availability, capacity, location)
  → Score assignments (distance, driver hours, client SLA)
  → Output: top-3 proposals with reasoning
  → Human approval → TMS create order
```

### 4.3 Fuel Agent

```
Input: fuel_level stream (ДУТ), GPS, CAN
  → Baseline model per vehicle (expected consumption)
  → Anomaly detection (sudden drop, off-route refuel)
  → Driver scoring (harsh braking, idle time)
  → Alert if confidence >= 0.85
  → Monthly savings report
```

### 4.4 Maintenance Agent

```
Input: odometer, engine hours, CAN DTC codes, history
  → Rules: interval-based (oil, tires, inspection)
  → ML: trend on vibration/temp (if available)
  → Output: maintenance schedule + 7-day forecast
```

---

## 5. Data model (core)

```mermaid
erDiagram
    Organization ||--o{ User : has
    Organization ||--o{ Vehicle : owns
    Organization ||--o{ Integration : configures
    Organization ||--o{ Order : manages

    Vehicle ||--o{ VehicleTelemetry : streams
    Vehicle ||--o{ FuelEvent : generates
    Vehicle ||--o{ MaintenanceTask : schedules

    Order ||--o{ RoutePlan : has
    RoutePlan ||--o{ RouteSegment : contains

    Integration {
        uuid id
        enum provider
        json credentials_enc
        enum status
        datetime last_sync
    }

    Vehicle {
        uuid id
        string plate
        json external_ids
        float capacity_kg
        enum status
    }

    FuelEvent {
        uuid id
        enum event_type
        float volume_liters
        float confidence
        datetime detected_at
    }
```

---

## 6. API surface (MVP)

```
# Integrations
POST   /api/v1/integrations              # Add connector
GET    /api/v1/integrations              # List connectors
POST   /api/v1/integrations/{id}/sync    # Force sync
GET    /api/v1/integrations/{id}/health  # Health check

# Fleet
GET    /api/v1/vehicles                  # List vehicles
GET    /api/v1/vehicles/{id}             # Vehicle detail
GET    /api/v1/vehicles/{id}/telemetry   # GPS + fuel history
GET    /api/v1/fleet/map                 # Real-time map data (SSE)

# Agents
POST   /api/v1/agents/route/optimize     # Route Agent
POST   /api/v1/agents/dispatch/process   # Dispatch Agent
GET    /api/v1/agents/fuel/alerts        # Fuel alerts
GET    /api/v1/agents/fuel/report        # Monthly report
GET    /api/v1/agents/maintenance/schedule

# Orders & Routes
POST   /api/v1/orders                    # Create/import order
GET    /api/v1/orders                    # List orders
POST   /api/v1/routes/{id}/approve       # Human approval

# Analytics
GET    /api/v1/analytics/roi             # ROI dashboard
GET    /api/v1/analytics/savings         # Savings breakdown

# Billing
POST   /api/v1/billing/checkout
GET    /api/v1/billing/usage
```

---

## 7. Tech stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, TypeScript, Tailwind, shadcn/ui, MapLibre |
| API | FastAPI, Pydantic v2 |
| Workers | Celery + Redis |
| DB | PostgreSQL 16 + TimescaleDB (telemetry) |
| Cache | Redis |
| Storage | Yandex S3 |
| Auth | Supabase Auth |
| LLM | Claude Sonnet (dispatch, explanations) |
| Optimization | OR-Tools (VRP) |
| Maps | Yandex Maps API, 2GIS fallback |
| Observability | Langfuse, Sentry, Grafana |

---

## 8. Security

- Credentials коннекторов: AES-256 encrypted at rest
- Tenant isolation: RLS по `organization_id`
- Audit log: все agent decisions + human approvals
- 152-ФЗ: Yandex Cloud ru-central1

---

## 9. Deployment (MVP lean)

**VPS 8 vCPU / 32GB RAM, Docker Compose** — до 10 клиентов, 500 ТС aggregate.

Scale path: K8s на Yandex Cloud при 50+ клиентах.

---

*Архитектура адаптирована из TenderPilot (startupp) с заменой document pipeline на Integration Hub + fleet agents.*
