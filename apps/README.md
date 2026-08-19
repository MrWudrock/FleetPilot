# FleetPilot — локальная разработка (Docker Compose)

```powershell
# из корня репозитория
.\dev.ps1
```

Сервисы:

| Сервис | URL |
|--------|-----|
| Web (Next.js) | http://localhost:3000 |
| Dashboard | http://localhost:3000/dashboard |
| API | http://localhost:8800 |
| OpenAPI | http://localhost:8800/docs |
| Health | http://localhost:8800/api/v1/health |
| Readiness | http://localhost:8800/api/v1/health/ready |
| DB meta | http://localhost:8800/api/v1/meta/db |
| Auth signup | POST http://localhost:8800/api/v1/auth/signup |
| Auth login | POST http://localhost:8800/api/v1/auth/login |
| ROI KPI | GET http://localhost:8800/api/v1/analytics/roi |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## Структура

```
apps/
├── api/          # FastAPI — Core API, Integration Hub (Sprint 2+)
│   └── app/
│       ├── main.py
│       ├── core/config.py
│       └── api/v1/
├── web/          # Next.js 15 — dashboard, fleet map UI
│   └── src/
│       ├── app/
│       ├── components/
│       └── lib/
└── desktop/      # Electron Windows client (NSIS installer)
agents/           # AI agents (подключаются к API в Sprint 2+)
landing/          # Маркетинговый сайт (Vercel) + /downloads/FleetPilot-Setup.exe
```

## Desktop (Windows)

```powershell
cd apps\desktop
npm install
npm run dist:win
# или из корня:
.\scripts\publish-desktop.ps1
```

Скачать с лендинга: `/downloads/FleetPilot-Setup.exe`. Подробности: [`apps/desktop/README.md`](desktop/README.md).

## Команды

```powershell
# Запуск всех сервисов
docker compose up --build

# Только инфраструктура (postgres + redis)
docker compose up postgres redis -d

# Логи API
docker compose logs -f api

# Остановка
docker compose down
```

## Миграции (Alembic)

Миграции применяются автоматически при старте API в Docker (`entrypoint.sh`).

```powershell
# Вручную (из apps/api, нужен запущенный postgres)
cd apps/api
alembic upgrade head

# Новая миграция после изменения моделей
alembic revision --autogenerate -m "describe change"
```

### Схема v1 (FP-2)

| Таблица | Назначение |
|---------|------------|
| `organizations` | Tenant (multi-tenant) |
| `users` | Пользователи org, роль RBAC (FP-4) |
| `vehicles` | Автопарк, `external_ids` для GPS |
| `integrations` | Коннекторы Omnicomm / СтавТРЭК |

Проверка: `GET /api/v1/meta/db` → `migration: "002"`, counts по таблицам.

### Auth (FP-3)

| Endpoint | Описание |
|----------|----------|
| `POST /api/v1/auth/signup` | Регистрация + создание org (роль admin) |
| `POST /api/v1/auth/login` | Вход, JWT bearer token |
| `GET /api/v1/auth/me` | Текущий пользователь (Authorization header) |
| `POST /api/v1/auth/invite` | Admin приглашает пользователя (token в Redis) |
| `POST /api/v1/auth/accept-invite` | Принятие приглашения + установка пароля |

Web UI: `/signup`, `/login`, `/accept-invite?token=...`, `/dashboard` (защищён).

### Demo seed (FP-7)

```powershell
.\dev.ps1
.\seed-demo.ps1
# Login: demo@fleetpilot.ru / Demo12345!
```

KPI data spec: [`docs/fleet-ai/KPI-DATA.md`](../docs/fleet-ai/KPI-DATA.md)

## Локально без Docker (опционально)

**API** (нужен Python 3.12+):

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL="postgresql://fleetpilot:fleetpilot@localhost:5432/fleetpilot"
$env:REDIS_URL="redis://localhost:6379/0"
uvicorn app.main:app --reload --port 8000
```

**Web** (нужен Node.js 20+):

```powershell
cd apps/web
npm install
$env:NEXT_PUBLIC_API_URL="http://localhost:8800"
npm run dev
```

## Sprint 1 roadmap (FP-1 … FP-8)

- [x] **FP-1** Monorepo + Docker Compose + health endpoints
- [x] **FP-2** PostgreSQL schema v1 (Organization, User, Vehicle, Integration)
- [x] **FP-3** Auth (signup/login, JWT, org invite)
- [x] **FP-4** RBAC — `require_roles()` dependency (базовый)
- [x] **FP-5** Dashboard KPI из API `/analytics/roi`
- [x] **FP-6** CI — `.github/workflows/app-ci.yml` (API compile + Docker, Web build)
- [x] **FP-7** Seed script (32 ТС demo + KPI data)
- [ ] **FP-8** Sentry + env config

См. [`docs/NEXT-STEPS.md`](../docs/NEXT-STEPS.md) и [`docs/fleet-ai/architecture.md`](../docs/fleet-ai/architecture.md).
