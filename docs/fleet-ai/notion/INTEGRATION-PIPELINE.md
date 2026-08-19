# FleetPilot — Integration Pipeline

> Linked view: **Backlog & Roadmap** → View «Integration Pipeline»

## Tier 1 — критичные (MVP)

| Provider | Статус | Задачи Backlog | Приоритет |
|----------|--------|----------------|-----------|
| **Wialon** (Local / Hosting) | Prototype → MVP | BL-009, BL-101–103 | P0 |
| **Omnicomm** | Discovery | BL-110 | P1 |
| **ТрансМенеджер** (TMS) | MVP (пилот) | BL-201–202 | P0 |
| **Росдормониторинг** | MVP (Permit) | BL-301–304 | P0 |

## Tier 2 — расширение

| Provider | Статус | Задачи | Приоритет |
|----------|--------|--------|-----------|
| СтавТРЭК | Idea | — | P2 |
| MSS GLONASS | Idea | — | P3 |
| Master TMS / ANTOR | Idea | — | P2 |
| Yandex Maps (routing) | Beta | Route Agent | P1 |

## Accounting & ERP

| Provider | Статус | Задачи | Приоритет |
|----------|--------|--------|-----------|
| **1С:Предприятие** | Discovery → Prototype | BL-010, BL-401 | P2 |
| CSV / Excel import | MVP (пилот) | BL-401 | P2 |
| HTTP-сервисы 1С | Scale | BL-402 | P3 |

## Internal

| Provider | Статус | Назначение |
|----------|--------|------------|
| Internal API | MVP | Core API FastAPI |
| Parser API (Росдор реестр) | MVP | urd.safe-route.ru |

## Порядок реализации (MVP)

```
1. Wialon Tier 1 (BL-009)
2. Карта realtime (BL-001)
3. ТрансМенеджер read (BL-201)
4. P&L / ROI (BL-004, BL-020)
5. Росдор Permit (BL-301)
6. 1С CSV (BL-401)
7. Omnicomm (BL-110) — post-MVP
```

## Риски интеграций

| Риск | Provider | Митигация |
|------|----------|-----------|
| LAN-only Wialon | Wialon Local | VPN / sync-agent |
| Нет REST API | ТрансМенеджер | ODBC / XML 15 min |
| Нет официального API | Росдор | Реестр + rule engine; Playwright фаза 2 |
| Долгое согласование | 1С | CSV в пилоте |
