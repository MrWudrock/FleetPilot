# FleetPilot — ИИ-агенты для транспортно-логистических компаний

Продуктовый пакет MVP: анализ российского рынка, PRD, архитектура, wireframes и landing.

**Production:** [fleetpilot.ru](https://fleetpilot.ru) · [wireframes](https://fleetpilot.ru/wireframes/) · [pitch-deck](https://fleetpilot.ru/pitch-deck)

## Быстрый старт

### Маркетинговый сайт (landing)

```powershell
# Локальный preview (Python — уже есть в Windows)
.\serve.ps1
# → http://localhost:8080/landing/
# → http://localhost:8080/wireframes/

# Или только landing
cd landing
.\serve.ps1
# → http://localhost:3000
```

### Приложение (monorepo · Sprint 1)

```powershell
# Требуется Docker Desktop
.\dev.ps1
# → http://localhost:3000        — Web
# → http://localhost:3000/dashboard
# → http://localhost:8800/docs  — API OpenAPI (порт 8800: на Windows Hyper-V часто резервирует :8000)
```

Подробнее: [`apps/README.md`](apps/README.md)

## Структура проекта

```
startapp log/
├── apps/                       # Monorepo приложения (FP-1+)
│   ├── api/                   # FastAPI — Core API
│   └── web/                   # Next.js 15 — dashboard
├── agents/                     # AI agents (Sprint 2+)
├── docker-compose.yml          # Postgres + Redis + API + Web
├── dev.ps1                     # docker compose up --build
├── landing/                    # Продакшен лендинг
│   ├── index.html             # Главная страница
│   ├── pitch-deck.html        # Pitch deck (12 слайдов)
│   ├── privacy.html           # Политика конфиденциальности
│   ├── terms.html             # Условия использования
│   ├── wireframes/            # MVP прототип (10 экранов)
│   ├── config.js              # Конфигурация (генерируется)
│   ├── config.example.js      # Пример конфигурации
│   ├── form.js                # Обработка форм
│   ├── analytics.js           # Яндекс.Метрика + GA4
│   ├── vercel.json            # Конфигурация Vercel
│   ├── deploy.ps1             # CLI деплой
│   └── .env.example           # Пример переменных окружения
├── wireframes/                 # Wireframes (корневая копия)
├── docs/fleet-ai/             # Документация
│   ├── PRD.md                 # Product Requirements Document
│   ├── architecture.md        # Архитектура системы
│   ├── competitive-analysis.md # Анализ рынка
│   ├── backlog-12-weeks.md    # Бэклог на 12 недель
│   └── pitch-deck.html        # Pitch deck (корневая копия)
├── scripts/                   # Утилиты
├── .github/workflows/         # CI/CD
│   ├── deploy.yml             # Production деплой
│   └── preview.yml            # PR preview
└── README.md
```

## Ключевая идея продукта

**Не конкурировать с AXELOT / «Умной логистикой» head-on**, а стать **ИИ-слоем поверх уже установленных систем**:

- GPS/ГЛОНАСС: Omnicomm, СтавТРЭК, MSS GLONASS
- TMS: Master TMS, ANTOR, Schedex
- Топливо: Omnicomm ДУТ, Era-Glonass
- WMS/YMS: AXELOT, ЯРД 2.0, FIRST

FleetPilot объединяет данные из существующих систем и автоматизирует **5 процессов** ИИ-агентами:

1. **Route Agent** — оптимизация маршрутов + интеграция мониторинга ТС
2. **Dispatch Agent** — приём заявок, классификация, назначение водителей
3. **Fuel Agent** — контроль топлива, сливы, стиль вождения
4. **Maintenance Agent** — предиктивное ТО
5. **Permit Agent** — спецразрешения негабарит + **Росдормониторинг** (NEW)

## Варианты названия проекта

| Название | Позиционирование | Плюсы |
|----------|------------------|-------|
| **FleetPilot** ★ | «Пилот вашего автопарка» | Параллель с TenderPilot, понятно ЛПР, короткий домен |
| **TransAgent** | ИИ-агенты для транспорта | Акцент на AI, tech-forward |
| **LogistMind** | «Умная логистика + ИИ» | Отсылка к рынку «Умная логистика» |
| **RouteForge** | Кузница маршрутов и экономии | Сильный акцент на оптимизацию |
| **АвтоПульс** | Российский бренд | Легко произносится |

## Документация

| Документ | Путь | Описание |
|----------|------|----------|
| **Запуск приложения** | [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | Docker / локально, demo-логин, troubleshooting |
| **Проверка demo / пилота** | [`docs/PILOT-TEST-GUIDE.md`](docs/PILOT-TEST-GUIDE.md) | Что работает в UI, как ввести данные Permit |
| **Анализ рынка** | [`docs/fleet-ai/competitive-analysis.md`](docs/fleet-ai/competitive-analysis.md) | Российские платформы, gaps, позиционирование |
| **PRD** | [`docs/fleet-ai/PRD.md`](docs/fleet-ai/PRD.md) | Product Requirements Document |
| **ТЗ MVP** | [`docs/fleet-ai/MVP-TZ.md`](docs/fleet-ai/MVP-TZ.md) | Контрактный срез MVP: scope, flows, приёмка |
| **PM Playbook** | [`docs/fleet-ai/PM-PLAYBOOK.md`](docs/fleet-ai/PM-PLAYBOOK.md) | Пошаговая работа Product Manager |
| **Архитектура** | [`docs/fleet-ai/architecture.md`](docs/fleet-ai/architecture.md) | Стек, интеграции, AI agents |
| **Backlog 12 нед.** | [`docs/fleet-ai/backlog-12-weeks.md`](docs/fleet-ai/backlog-12-weeks.md) | 6 спринтов, 65 tickets, ~188 SP |
| **Pitch deck** | [`docs/fleet-ai/pitch-deck.html`](docs/fleet-ai/pitch-deck.html) | 12 слайдов · ← → навигация |
| **Wireframes** | [`wireframes/index.html`](wireframes/index.html) | 10 ключевых экранов MVP |
| **Следующие шаги** | [`docs/NEXT-STEPS.md`](docs/NEXT-STEPS.md) | Стадия 1: Sprint 1 Foundation |
| **Первая встреча** | [`docs/fleet-ai/FIRST-MEETING-GUIDE.md`](docs/fleet-ai/FIRST-MEETING-GUIDE.md) | Discovery + ТЗ |
| **Росдормониторинг** | [`docs/fleet-ai/ROSDORMONITORING-INTEGRATION.md`](docs/fleet-ai/ROSDORMONITORING-INTEGRATION.md) | Permit Agent |
| **Sales Playbook** | [`docs/fleet-ai/SALES-PLAYBOOK-RU.md`](docs/fleet-ai/SALES-PLAYBOOK-RU.md) | Воронка B2B РФ |

## Экономика (целевой ICP)

- **ICP:** транспортные компании, 20–50 ТС, ₽10–15M операционный бюджет/год
- **Инвестиции MVP-клиента:** ₽630K (Этап 1) → ₽2.55M (полная интеграция)
- **Годовая экономия:** до ₽3.21M (ROI 126%, окупаемость ~9.5 мес.)
- **Founding offer:** ₽49K/мес × 6 мес · до 30 ТС · onboarding бесплатно

## Деплой на Vercel

### Способ 1 — GitHub (рекомендуется)

1. Создайте репозиторий на GitHub
2. Push проекта
3. [vercel.com/new](https://vercel.com/new) → Import repository
4. **Root Directory:** `landing`
5. **Build Command:** `node generate-config.js`
6. **Output Directory:** `.`
7. Environment Variables:

| Variable | Описание |
|----------|----------|
| `SITE_URL` | `https://fleetpilot.ru` |
| `SUPPORT_EMAIL` | `hello@fleetpilot.ru` |
| `FORMSPREE_ID` | ID Formspree |
| `YANDEX_METRIKA_ID` | Счётчик Метрики |
| `GA4_MEASUREMENT_ID` | GA4 Measurement ID |

### Способ 2 — CLI

```powershell
cd landing
.\sync-assets.ps1
.\deploy.ps1
```

### Домен fleetpilot.ru

1. Vercel → Settings → Domains → Add `fleetpilot.ru`
2. DNS у регистратора:
   - **A** `@` → `76.76.21.21`
   - **CNAME** `www` → `cname.vercel-dns.com`
3. SSL автоматический (Let's Encrypt)

Подробнее: [`landing/VERCEL-DEPLOY.md`](landing/VERCEL-DEPLOY.md), [`landing/DOMAIN.md`](landing/DOMAIN.md)

## CI/CD

GitHub Actions автоматически деплоят при push в `main`:

- **Production:** при изменении файлов в `landing/`
- **Preview:** при pull request

Требуемые secrets в GitHub:
- `VERCEL_TOKEN` — токен Vercel
- `VERCEL_ORG_ID` — ID организации
- `VERCEL_PROJECT_ID` — ID проекта

## Переменные окружения

Скопируйте `landing/.env.example` в `landing/.env` и заполните:

```powershell
copy landing\.env.example landing\.env
```

## Страницы на домене

| URL | Страница |
|-----|----------|
| `https://fleetpilot.ru/` | Landing |
| `https://fleetpilot.ru/wireframes/` | MVP прототип |
| `https://fleetpilot.ru/pitch-deck` | Pitch deck |
| `https://fleetpilot.ru/privacy` | Политика конфиденциальности |
| `https://fleetpilot.ru/terms` | Условия использования |
| `https://fleetpilot.ru/sitemap.xml` | Sitemap |
| `https://fleetpilot.ru/robots.txt` | Robots |

## Лицензия

Проект является проприетарным ПО. Все права защищены.
