# FleetPilot — ИИ-агенты для транспортно-логистических компаний

Продуктовый пакет MVP: анализ российского рынка, PRD, архитектура, wireframes и landing.

**Рекомендуемое название:** **FleetPilot** (альтернативы — см. ниже)

## Варианты названия проекта

| Название | Позиционирование | Плюсы |
|----------|------------------|-------|
| **FleetPilot** ★ | «Пилот вашего автопарка» | Параллель с TenderPilot, понятно ЛПР, короткий домен |
| **TransAgent** | ИИ-агенты для транспорта | Акцент на AI, tech-forward |
| **LogistMind** | «Умная логистика + ИИ» | Отсылка к рынку «Умная логистика», но дифференциация через agents |
| **RouteForge** | Кузница маршрутов и экономии | Сильный акцент на оптимизацию и ROI |
| **АвтоПульс** | Российский бренд, «пульс автопарка» | Легко произносится, не требует англ. |

## Ключевая идея продукта

**Не конкурировать с AXELOT / «Умной логистикой» head-on**, а стать **ИИ-слоем поверх уже установленных систем**:

- GPS/ГЛОНАСС: Omnicomm, СтавТРЭК, MSS GLONASS
- TMS: Master TMS, ANTOR, Schedex
- Топливо: Omnicomm ДУТ, Era-Glonass
- WMS/YMS: AXELOT, ЯРД 2.0, FIRST

FleetPilot объединяет данные из существующих систем и автоматизирует 4 процесса ИИ-агентами:

1. **Route Agent** — оптимизация маршрутов + интеграция мониторинга ТС
2. **Dispatch Agent** — приём заявок, классификация, назначение водителей
3. **Fuel Agent** — контроль топлива, сливы, стиль вождения
4. **Maintenance Agent** — предиктивное ТО

## Файлы

| Документ | Путь | Описание |
|----------|------|----------|
| **Анализ рынка** | [`docs/fleet-ai/competitive-analysis.md`](docs/fleet-ai/competitive-analysis.md) | Российские платформы, gaps, позиционирование |
| **PRD** | [`docs/fleet-ai/PRD.md`](docs/fleet-ai/PRD.md) | Product Requirements Document |
| **Архитектура** | [`docs/fleet-ai/architecture.md`](docs/fleet-ai/architecture.md) | Стек, интеграции, AI agents |
| **Backlog 12 нед.** | [`docs/fleet-ai/backlog-12-weeks.md`](docs/fleet-ai/backlog-12-weeks.md) | 6 спринтов, 65 tickets, ~188 SP |
| **Linear import** | [`docs/fleet-ai/backlog-linear-import.csv`](docs/fleet-ai/backlog-linear-import.csv) | CSV для Linear |
| **Jira import** | [`docs/fleet-ai/backlog-jira-import.csv`](docs/fleet-ai/backlog-jira-import.csv) | CSV для Jira ([инструкция](docs/fleet-ai/JIRA-IMPORT.md)) |
| **Pitch deck** | [`docs/fleet-ai/pitch-deck.html`](docs/fleet-ai/pitch-deck.html) | 12 слайдов · ← → навигация |
| **Wireframes** | [`wireframes/index.html`](wireframes/index.html) | 10 ключевых экранов MVP |
| **Landing** | [`landing/index.html`](landing/index.html) | Лендинг + форма заявки |
| **Vercel deploy** | [`landing/VERCEL-DEPLOY.md`](landing/VERCEL-DEPLOY.md) | Деплой на Vercel |

## Быстрый старт

Node.js **не обязателен** — достаточно Python (уже есть в Windows) или двойной клик по HTML.

```powershell
# Вариант 1 — сервер из корня (landing + wireframes + docs)
.\serve.ps1
# → http://localhost:8080/landing/
# → http://localhost:8080/wireframes/

# Вариант 2 — только landing
cd landing
.\serve.ps1
# → http://localhost:3000

# Вариант 3 — без сервера (быстрый просмотр)
start wireframes\index.html
start landing\index.html
```

Если установите Node.js позже: `cd landing && npx serve .`

## Экономика (целевой ICP)

- **ICP:** транспортные компании, 20–50 ТС, ₽10–15M операционный бюджет/год
- **Инвестиции MVP-клиента:** ₽630K (Этап 1) → ₽2.55M (полная интеграция)
- **Годовая экономия:** до ₽3.21M (ROI 126%, окупаемость ~9.5 мес.)
- **Founding offer:** ₽49K/мес × 6 мес · до 30 ТС · onboarding бесплатно

## Deploy landing (Vercel)

**Подробно:** [`landing/VERCEL-DEPLOY.md`](landing/VERCEL-DEPLOY.md)

```powershell
cd landing
.\sync-assets.ps1          # wireframes + pitch-deck → landing/
.\deploy.ps1                 # нужен Node.js
```

**Без Node.js локально:** GitHub → [vercel.com/new](https://vercel.com/new) → Root Directory: `landing` → Build: `node generate-config.js`

Env: `FORMSPREE_ID`, `FORM_SUBMIT_EMAIL`, `YANDEX_METRIKA_ID`

**URLs на Vercel:** `/` · `/wireframes` · `/pitch-deck`
