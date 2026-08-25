# FleetPilot — инструкция по сборке в Notion

## Структура workspace

```
📄 FleetPilot — Product Plan          ← главная (скопировать из PRODUCT-PLAN.md)
├── 🗃️ FleetPilot — Backlog & Roadmap   ← Import product-backlog.csv
├── 🗃️ FleetPilot — Discovery           ← Import discovery.csv
└── 📄 FleetPilot — Integration Pipeline ← скопировать из INTEGRATION-PIPELINE.md
```

## Шаг 1. Главная страница

1. Notion → **New page** → название: `FleetPilot — Product Plan`
2. Скопируйте содержимое [`PRODUCT-PLAN.md`](PRODUCT-PLAN.md) секция за секцией (или вставьте Markdown через Notion import)
3. Добавьте **Linked database** views внизу страницы (после создания баз)

## Шаг 2. Backlog & Roadmap

1. **New page** → `/table` → **Full page database** → `FleetPilot — Backlog & Roadmap`
2. **⋯ → Merge with CSV** → загрузите [`product-backlog.csv`](product-backlog.csv)
3. После импорта настройте типы полей:

| CSV-колонка | Тип Notion |
|-------------|------------|
| Name | Title |
| Type | Select |
| Status | Select |
| Stage | Select |
| Product Area | Select |
| Priority | Select |
| Impact | Number |
| Effort | Number |
| Reach | Number |
| Confidence | Number |
| RICE Score | Number (или Formula) |
| Integration Provider | Multi-select |
| Vehicle Segment | Select |
| Tariff Segment | Select |
| Tariff Plan | Select |
| Model/AI Usage | Multi-select |
| API Exposure | Select |
| Discovery Link | Text → потом заменить на **Relation** |
| Description | Text |
| Acceptance Criteria | Text |
| Due date | Date |
| Owner | Person |

4. **Formula RICE** (если хотите пересчёт в Notion):
   ```
   prop("Reach") * prop("Impact") * prop("Confidence") / prop("Effort")
   ```

5. Создайте **Relation** `Linked: Discovery` → база Discovery (двусторонняя `Linked Features`)

6. Сопоставьте `Discovery Link` (DIS-001 …) вручную или через Notion AI

### Views для Backlog

| View | Тип | Фильтр / сортировка |
|------|-----|---------------------|
| Backlog | Table | Stage ≠ Scale; Sort Priority, RICE ↓ |
| MVP FleetPilot | Kanban | Stage contains MVP; group Status |
| MVP Scope | Table | Stage = MVP AND Priority = P0 or P1 |
| Roadmap | Timeline | Due date not empty; color by Stage |
| Board – Status | Board | group by Status |
| Telematics Integrations | Table | Product Area = Telematics OR Integrations |
| Financial Analytics | Table | Product Area contains Financial |
| Tariffs & Billing | Table | Product Area contains Billing |
| Integration Pipeline | Board | Product Area = Integrations; group Integration Provider; sort Stage |

## Шаг 3. Discovery

1. **New page** → `/table` → `FleetPilot — Discovery`
2. Import [`discovery.csv`](discovery.csv)
3. Поля:

| CSV-колонка | Тип Notion |
|-------------|------------|
| Name | Title |
| Type | Select |
| Segment | Select |
| Fleet Size | Number |
| Country/Region | Select |
| Use Case Type | Select |
| Pain Type | Multi-select |
| Tools currently used | Multi-select |
| Status | Select |
| Confidence | Number |
| Linked Features | Text → Relation после связи с Backlog |
| Notes | Text |

### Views для Discovery

| View | Фильтр |
|------|--------|
| Hypotheses | Type = Hypothesis |
| Interviews | Type = Interview |
| Validated insights | Status = Validated |
| Competitors | Type = Competitor |
| Pilot 6 TC | Segment contains Pilot |

## Шаг 4. Templates в Notion

### Feature template (Backlog)

См. [`TEMPLATES.md`](TEMPLATES.md) → скопировать в Notion Template button

### Hypothesis template (Discovery)

См. [`TEMPLATES.md`](TEMPLATES.md)

## Шаг 5. Integration Pipeline page

Создайте страницу `FleetPilot — Integration Pipeline`, вставьте содержимое [`INTEGRATION-PIPELINE.md`](INTEGRATION-PIPELINE.md), добавьте **Linked view** Backlog с фильтром Integration Pipeline.

## Шаг 6. Связать с главной

На `FleetPilot — Product Plan` добавьте:

- Linked view: **MVP FleetPilot** (Kanban)
- Linked view: **Roadmap** (Timeline)
- Linked view: **Validated insights** (Discovery)
- Toggle «Как пользоваться» — текст из PRODUCT-PLAN.md

---

*Импорт CSV: Notion может объединить похожие Select-значения — проверьте опечатки (Telemtics → Telematics).*
