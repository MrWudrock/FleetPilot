# FleetPilot — инструкция для Product Manager

**Версия:** 1.0 · **Дата:** 13.07.2026  
**Аудитория:** Product Manager (и PM-совмещение founder/lead)  
**Горизонт:** discovery → MVP → пилот → paid → scale

---

## Содержание

1. [Роль PM и зона ответственности](#1-роль-pm-и-зона-ответственности)
2. [Инструменты и артефакты](#2-инструменты-и-артефакты)
3. [Фаза 0 — Подготовка (неделя 0)](#3-фаза-0--подготовка-неделя-0)
4. [Фаза 1 — Discovery и квалификация (недели 1–2)](#4-фаза-1--discovery-и-квалификация-недели-12)
5. [Фаза 2 — Scope пилота и backlog (недели 2–3)](#5-фаза-2--scope-пилота-и-backlog-недели-23)
6. [Фаза 3 — Контракт и доступы (неделя 3)](#6-фаза-3--контракт-и-доступы-неделя-3)
7. [Фаза 4 — Ведение пилота (недели 4–10)](#7-фаза-4--ведение-пилота-недели-410)
8. [Фаза 5 — Приёмка и конверсия в paid (недели 10–12)](#8-фаза-5--приёмка-и-конверсия-в-paid-недели-1012)
9. [Фаза 6 — Post-pilot и roadmap (ongoing)](#9-фаза-6--post-pilot-и-roadmap-ongoing)
10. [Еженедельный ритм PM](#10-еженедельный-ритм-pm)
11. [Матрица решений (что эскалировать)](#11-матрица-решений-что-эскалировать)
12. [Чеклисты по ролям стейкхолдеров](#12-чеклисты-по-ролям-стейкхолдеров)
13. [Связанные документы](#13-связанные-документы)

---

## 1. Роль PM и зона ответственности

### Что делает PM в FleetPilot

| Зона | PM отвечает за | Не делает PM (делегирует) |
|------|----------------|---------------------------|
| **Продукт** | Vision, scope MVP, приоритеты backlog, acceptance criteria | Написание production-кода |
| **Discovery** | Интервью, гипотезы, валидация болей, ICP | Юридическое заключение по 152-ФЗ |
| **Пилот** | KPI, baseline, еженедельные статусы, риски | Настройка VPN на стороне клиента |
| **Delivery** | Спринты, unblock, приёмка фич по AC | DevOps 24/7 on-call |
| **GTM** | Demo-сценарии, case study, pricing input | Холодные продажи без SQL |
| **Метрики** | North Star, activation, отчёт пилота | Бухгалтерия и выставление счетов |

### North Star (запомнить)

**Подтверждённая экономия ₽/мес** (ROI dashboard) + **активные машины с телематикой и регулярным использованием кабинета**.

### Текущий фокус продукта

- **Продукт:** fleet SaaS (телематика + P&L + utilization) + **5 ИИ-агентов**
- **Пилот #1:** 6 ТС, Wialon Local, ТрансМенеджер, Росдормониторинг, 1С
- **Дифференциатор:** Permit Agent + надстройка над legacy, не замена

---

## 2. Инструменты и артефакты

### Обязательный стек PM

| Инструмент | Назначение | Где лежит |
|------------|------------|-----------|
| **Notion** | Product Plan, Backlog, Discovery | [`notion/NOTION-SETUP.md`](notion/NOTION-SETUP.md) |
| **GitHub** | Issues, PR, docs, CI | Репозиторий FleetPilot |
| **Linear / Jira** (опционально) | Спринты dev | [`LINEAR-IMPORT.md`](LINEAR-IMPORT.md), [`JIRA-IMPORT.md`](JIRA-IMPORT.md) |
| **Figma / wireframes** | Demo UI | `wireframes/` |
| **fleetpilot.ru** | Лендинг, inbound | `landing/` |

### Артефакты, которые PM обязан вести

| Артефакт | Когда создаётся | Шаблон |
|----------|-----------------|--------|
| Протокол discovery-встречи | После каждой встречи (24 ч) | [`meeting-protocol-template.md`](meeting-protocol-template.md) |
| One-pager пилота | После согласования scope | [`PRODUCT-PLAN.md`](notion/PRODUCT-PLAN.md) §4 |
| Карта интеграций | Неделя 1 пилота | [`INTEGRATION-PIPELINE.md`](notion/INTEGRATION-PIPELINE.md) |
| KPI baseline | До старта пилота | §7.4 ниже |
| Weekly pilot status | Каждую пятницу | §10 |
| Отчёт приёмки пилота | Неделя 10–12 | §8 |

### Первый день PM: настройка Notion

- [ ] Импортировать [`product-backlog.csv`](notion/product-backlog.csv) и [`discovery.csv`](notion/discovery.csv)
- [ ] Создать views: MVP FleetPilot, Roadmap, Integration Pipeline
- [ ] Скопировать главную страницу из [`PRODUCT-PLAN.md`](notion/PRODUCT-PLAN.md)
- [ ] Назначить Owner на P0-задачи текущего спринта

---

## 3. Фаза 0 — Подготовка (неделя 0)

**Цель:** PM понимает продукт, ICP и текущее состояние кода; workspace готов.

### Задачи PM (пошагово)

| # | Задача | Действие | Done когда |
|---|--------|----------|------------|
| 0.1 | Изучить продукт | Прочитать PRD, architecture, PRODUCT-PLAN | Можешь объяснить 5 агентов за 3 мин |
| 0.2 | Изучить ICP | SALES-PLAYBOOK, competitive-analysis | Знаешь disqualify-критерии |
| 0.3 | Поднять demo локально | `docker compose up -d postgres redis api`, demo login | Health OK на `:8800` |
| 0.4 | Пройти Permit API | `.\scripts\verify_permit_api.ps1` | Все checks passed |
| 0.5 | Настроить Notion | NOTION-SETUP.md | 3 сущности + 5 views |
| 0.6 | Синхронизация с eng | 30 мин с tech lead: что Released, что In MVP | Список блокеров |
| 0.7 | Определить текущий пилот | Имя клиента, 6 ТС, контакты, дата kickoff | Карточка в Discovery |

### Выход фазы

- [ ] Notion workspace live
- [ ] Demo org работает
- [ ] Список P0 на ближайшие 2 недели согласован с разработкой

---

## 4. Фаза 1 — Discovery и квалификация (недели 1–2)

**Цель:** подтвердить fit клиента, собрать боли, зафиксировать baseline.

### 4.1 До встречи (за 1–2 дня)

| # | Задача | Детали |
|---|--------|--------|
| 1.1 | Desk research | Сайт клиента, тип ТС, регионы, негабарит? |
| 1.2 | Проверить стек | Wialon / Omnicomm, TMS, Росдор ЛК, 1С |
| 1.3 | Подготовить agenda | 45–60 мин, [`FIRST-MEETING-GUIDE.md`](FIRST-MEETING-GUIDE.md) |
| 1.4 | Открыть протокол | `meeting-protocol-template.md` |
| 1.5 | Подготовить 2–3 demo-сценария | Карта → заявка → Permit analyze (если негабарит) |

### 4.2 На встрече (структура 45–60 мин)

| Блок | Время | Вопросы PM |
|------|-------|------------|
| Открытие | 5 мин | Цель, роли, запись |
| Бизнес-контекст | 10 мин | ТС, боль #1, триггер «почему сейчас» |
| Процесс as-is | 10 мин | Заявка → рейс → разрешение → 1С |
| Технический контур | 10 мин | API, 152-ФЗ, кто IT |
| MVP / пилот | 10 мин | Must-have vs later, KPI успеха |
| Закрытие | 5 мин | Следующие шаги, дата follow-up |

### 4.3 После встречи (в тот же день + 48 ч)

| # | Задача | Срок |
|---|--------|------|
| 1.6 | Протокол встречи | 4 ч |
| 1.7 | Запись в Discovery (Type=Interview) | 4 ч |
| 1.8 | 3–5 гипотез в Discovery | 24 ч |
| 1.9 | Письмо клиенту: резюме + открытые вопросы | 24–48 ч |
| 1.10 | BANT-квалификация | 48 ч |

**BANT для FleetPilot:**

| Критерий | Go | No-go |
|----------|-----|-------|
| Budget | IT ₽300K+/год или готовность Founding ₽49K×6 | «Нет бюджета» |
| Authority | ЛПР на встрече или intro | «Передам начальнику» без даты |
| Need | GPS + боль (топливо/dispatch/permit) | «Просто посмотреть» |
| Timeline | Решение ≤90 дней | «Когда-нибудь» |
| Fleet | ≥5 ТС с телематикой | Нет GPS |

### 4.4 Задачи в Notion после discovery

- [ ] Создать Interview в Discovery → Status `In progress` / `Validated`
- [ ] Связать гипотезы с backlog-фичами (Relation)
- [ ] Если pilot fit — создать Experiment `DIS-012` и задачи BL-701, BL-702

---

## 5. Фаза 2 — Scope пилота и backlog (недели 2–3)

**Цель:** зафиксирован scope, KPI, порядок delivery; backlog приоритизирован.

### 5.1 One-pager пилота (PM пишет, ЛПР подписывает)

Включить обязательно:

1. **Клиент:** название, 6 ТС, стек (Wialon Local, ТМ, Росдор, 1С)
2. **Срок:** 6–8 недель, даты kickoff / приёмка
3. **Scope in:** таблица из PRODUCT-PLAN §4.3
4. **Scope out:** Playwright urm, API 1С, биллинг, web mobile
5. **KPI** (см. §5.2)
6. **Команда клиента:** admin, dispatcher, IT, негабарит (если есть)
7. **Команда FleetPilot:** PM, eng, support

### 5.2 KPI пилота — зафиксировать baseline ДО старта

| Метрика | Как измерять | Baseline (заполнить) | Target |
|---------|--------------|----------------------|--------|
| Время обработки заявки | Хронометраж диспетчера, 5 заявок | ___ мин | −30–50% |
| Время на спецразрешение | От заявки до черновика в Росдор | ___ ч | −40–60% |
| Ошибки/переделки разрешений | Шт/мес | ___ | → 0 в пилоте |
| Расход топлива | л/100 км по Wialon | ___ | −5–10% |
| Ручной ввод между системами | раз/день | ___ | −70% |
| WAU диспетчеров | лог FleetPilot | 0 | 2/2, 4+ нед |
| % заявок через FP | заявки ТМ vs обработанные в FP | 0% | ≥70% |

### 5.3 Приоритизация backlog (PM + eng)

Использовать порядок из PRODUCT-PLAN §7:

1. BL-009 Wialon → 2. BL-001 карта → 3. BL-201 ТМ → 4. BL-004 P&L → 5. BL-301 Permit → …

**Правило PM:** не менять порядок Tier 1 интеграции без архитектурной причины.

### 5.4 Спринт-планирование (пример 2-нед спринт)

| Спринт | Цель | P0 задачи |
|--------|------|-----------|
| S1 | Интеграции live | BL-009, BL-102, BL-103, BL-201 |
| S2 | Витрина + Permit | BL-001, BL-301–303, BL-202 |
| S3 | Аналитика + Fuel | BL-004, BL-020, BL-501, BL-006 |
| S4 | Стабилизация + приёмка | BL-305, BL-401, BL-704 |

### 5.5 Definition of Ready (DoR) для фичи

Фича идёт в In Progress только если:

- [ ] Есть Problem + User Story + AC в карточке backlog
- [ ] Связана с Discovery (≥1)
- [ ] Priority и Stage проставлены
- [ ] Eng оценил Effort
- [ ] Зависимости (интеграции) отмечены

### 5.6 Definition of Done (DoD) для фичи

- [ ] AC выполнены и проверены PM
- [ ] Демо на staging/demo org
- [ ] Документация обновлена (если API)
- [ ] Status → Ready for Release / Released
- [ ] Клиенту не ломает пилот (regression)

---

## 6. Фаза 3 — Контракт и доступы (неделя 3)

**Цель:** юридически и технически готовы к kickoff.

### Чеклист PM

| # | Задача | Ответственный | Артефакт |
|---|--------|---------------|----------|
| 3.1 | NDA подписан | Юрист / ЛПР | BL-702 |
| 3.2 | Договор пилота / 152-ФЗ | Юрист | DPA |
| 3.3 | Kickoff meeting назначен | PM | Calendar |
| 3.4 | Запрос доступов Wialon | IT клиента | token, unit list |
| 3.5 | Запрос доступов ТМ | IT клиента | API или формат выгрузки |
| 3.6 | ЛК Росдор | Диспетчер | urm.safe-route.ru |
| 3.7 | 1С: формат CSV | Бухгалтерия | шаблон полей |
| 3.8 | VPN (если Wialon Local) | IT клиента + DevOps | BL-101 |
| 3.9 | Champion-диспетчер named | ЛПР | имя, Telegram |
| 3.10 | KPI baseline снят | PM + диспетчер | таблица §5.2 |

### Карта интеграций (PM заполняет)

| Система | URL / тип | Статус | Риск | Owner клиента |
|---------|-----------|--------|------|---------------|
| Wialon Local | | | | |
| ТрансМенеджер | | | | |
| Росдор | urm / urd | | | |
| 1С | CSV / API | | | |

### Kickoff agenda (60 мин)

1. Цели пилота и KPI (10 мин)
2. Scope in/out (10 мин)
3. Роли и коммуникации (10 мин)
4. Доступы и timeline (15 мин)
5. Еженедельный ритм (5 мин)
6. Q&A (10 мин)

**После kickoff:** обновить BL-701 → Released, отправить summary письмом.

---

## 7. Фаза 4 — Ведение пилота (недели 4–10)

**Цель:** delivery по roadmap, еженедельная обратная связь, риски под контролем.

### 7.1 Недельный план PM

| День | Действие PM |
|------|-------------|
| **Пн** | Проверить статус интеграций (health); обновить Notion backlog |
| **Вт** | Sync с eng 15–30 мин: блокеры, scope creep |
| **Ср** | Созвон с клиентом 30 мин (champion + IT при необходимости) |
| **Чт** | Приёмка готовых фич по AC; UAT на demo org |
| **Пт** | Weekly pilot status → ЛПР; обновить KPI tracker |

### 7.2 Контрольные точки пилота (milestones)

| Неделя | Milestone | Критерий приёмки PM |
|--------|-----------|---------------------|
| 4 | Wialon live | 6/6 ТС на карте, latency <5 мин |
| 5 | ТМ + заявки | Список заявок в UI, ≥1 sync cycle OK |
| 6 | Permit E2E | 3/5 маршрутов analyze → approve |
| 7 | P&L / ROI | Dashboard с данными пилота |
| 8 | Fuel + 1С CSV | ≥1 алерт + 1 сверка CSV |
| 9 | Обучение | 2 пользователя trained (BL-703) |
| 10 | 5/5 Permit + отчёт | BL-305, BL-704 draft |

### 7.3 UAT-сценарии (PM прогоняет каждую неделю)

**Сценарий A — Телематика**
1. Открыть карту → все 6 ТС видны
2. Статус «в движении» соответствует Wialon
3. Пробег за неделю > 0

**Сценарий B — Заявка**
1. Новая заявка в ТМ → появляется в FleetPilot ≤15 мин
2. Поля А→Б, габариты заполнены

**Сценарий C — Permit (негабарит)**
1. POST analyze-route → `permit_required=true`
2. Диспетчер approve → audit log
3. Check реестра DEMO/API

**Сценарий D — Fuel**
1. Baseline отображается
2. Сгенерировать/дождаться алерта → диспетчер видит в UI

**Сценарий E — ROI**
1. Dashboard показывает savings breakdown
2. Цифры согласуются с baseline-гипотезой

### 7.4 Работа с рисками в пилоте

| Риск | Сигнал | Действие PM |
|------|--------|-------------|
| Wialon недоступен | health red | Эскалация IT клиента; VPN ticket |
| ТМ без API | задержка >1 нед | Scope: XML 15 min; зафиксировать в one-pager |
| Диспетчер не заходит | WAU 0 | Доп. обучение; упростить UI path |
| Scope creep | «А можно ещё…» | Backlog Idea; не в пилот без change request |
| Нет негабарита за период | Permit KPI пустой | 5 исторических маршрутов retro |

### 7.5 Change Request (если клиент просит вне scope)

1. Зафиксировать запрос в Notion (Status=Idea)
2. Оценить Effort с eng
3. Предложить: в пилот (swap) / post-pilot / paid change
4. ЛПР подписывает изменение one-pager

---

## 8. Фаза 5 — Приёмка и конверсия в paid (недели 10–12)

**Цель:** отчёт пилота, решение о контракте, handoff в Customer Success.

### 8.1 Отчёт приёмки пилота (структура)

1. **Executive summary** (½ стр): достигли ли KPI, рекомендация
2. **Метрики** — таблица baseline vs fact
3. **Что сделано** — scope checklist
4. **Инциденты** — что сломалось, как починили
5. **Цитаты пользователей** — 2–3 от диспетчера/ЛПР
6. **ROI** — ₽ эквивалент или время
7. **Recommendation** — Pro / доработка / stop
8. **Roadmap фазы 2** — 3–5 пунктов

### 8.2 Задачи PM при приёмке

| # | Задача |
|---|--------|
| 8.1 | Заполнить KPI fact в таблице §5.2 |
| 8.2 | Провести приёмочную встречу 60 мин с ЛПР |
| 8.3 | Получить письменное согласие/замечания (email) |
| 8.4 | Обновить BL-704 → Released |
| 8.5 | Case study draft (с разрешения клиента) |
| 8.6 | КП на Pro / Founding (с Sales) |
| 8.7 | Discovery: Experiment DIS-012 → Validated / Invalidated |

### 8.3 Критерии успеха пилота (go/no-go paid)

| | Go paid | No-go |
|---|---------|-------|
| KPI время заявки/разрешения | ≥−25% | <−10% |
| WAU диспетчеров | 2/2 | 0–1 |
| Интеграции | Wialon + ТМ stable | постоянные outages |
| NPS champion | ≥7 | ≤5 |
| ЛПР feedback | «готовы платить» | «вернёмся позже» без даты |

### 8.4 Конверсия в тариф

| Исход пилота | Тариф | Следующий шаг PM |
|--------------|-------|------------------|
| 6 ТС, все агенты | Pro Founding ₽49K | Onboarding billing (post-MVP) |
| Только телематика | Basic | Upsell Permit через 3 мес |
| Enterprise запрос | Custom | Roadmap 1С API, SLA |

---

## 9. Фаза 6 — Post-pilot и roadmap (ongoing)

### 9.1 Quarterly planning (PM раз в квартал)

| # | Задача |
|---|--------|
| 9.1 | Review North Star по всем клиентам |
| 9.2 | Обновить ICP по Discovery Validated |
| 9.3 | Пересчитать RICE топ-20 backlog |
| 9.4 | Согласовать Stage: Beta → Launch → Scale |
| 9.5 | Обновить PRODUCT-PLAN и competitive-analysis |

### 9.2 Приоритеты post-MVP (очередность PM)

1. Permit фаза 2 — Playwright urm (BL-802)
2. Omnicomm Tier 1 (BL-110)
3. 1С HTTP API (BL-402)
4. ЮKassa billing
5. Public API (BL-801)
6. Web UI полный (не только API)

### 9.3 Работа с backlog (ongoing правила)

- Новая идея → Status `Idea`, не в спринт без Discovery link
- Bug в пилоте → P0 если блокирует UAT; иначе P1
- Каждый спринт: max 2 интеграции одновременно (фокус)
- Released → анонс в weekly клиенту

---

## 10. Еженедельный ритм PM

### Понедельник — Planning lite (30 мин solo + 15 с eng)

- [ ] Backlog board: что In Progress / blocked
- [ ] 3 приоритета недели (написать в Notion / Slack)
- [ ] Проверить Due dates Roadmap view

### Среда — Клиент (30 мин)

**Agenda:**
1. Что нового в продукте (2 мин)
2. Инциденты (5 мин)
3. Обратная связь champion (15 мин)
4. Следующая неделя (5 мин)
5. Блокеры доступов (3 мин)

### Пятница — Status report (шаблон письма ЛПР)

```
Тема: FleetPilot Pilot — Week N Status

✅ Сделано на этой неделе:
- …

📊 KPI snapshot:
- Заявок через FP: …
- Permit маршрутов: …
- WAU: …

⚠️ Риски / блокеры:
- …

📅 На следующей неделе:
- …

Нужно от вас:
- …
```

### Ежемесячно — Product review (60 мин internal)

- Метрики: North Star, activation, retention
- Top 5 Discovery insights
- Roadmap adjustments
- Demo новых фич команде

---

## 11. Матрица решений (что эскалировать)

| Ситуация | PM решает сам | Эскалация founder / eng lead |
|----------|---------------|------------------------------|
| Приоритет P2 vs P3 | ✅ | |
| Изменение AC фичи | ✅ | |
| Scope creep в пилоте | ✅ (change request) | если ЛПР настаивает на P0 вне scope |
| Отключение фичи из MVP | | ✅ |
| Скидка >20% | | ✅ |
| Хостинг не РФ | | ✅ |
| Playwright Росдор (юридика) | | ✅ + юрист |
| Технический dead-end интеграции >1 нед | | ✅ |

---

## 12. Чеклисты по ролям стейкхолдеров

### Что PM запрашивает у **ЛПР клиента**

- [ ] Подписант пилота / бюджет
- [ ] Champion-диспетчер (имя, контакт)
- [ ] KPI baseline 30 мин их времени
- [ ] Участие в приёмке неделя 10–12

### Что PM запрашивает у **IT клиента**

- [ ] Wialon token + unit list
- [ ] ТМ API / выгрузка
- [ ] VPN (если Local)
- [ ] Контакт для инцидентов (SLA ответа 24 ч)

### Что PM запрашивает у **диспетчера**

- [ ] 2 ч обучение
- [ ] 5 исторических маршрутов негабарита
- [ ] Еженедельная обратная связь 15 мин
- [ ] HITL approve в Permit

### Что PM отдаёт **разработке**

- [ ] DoR-карточки с AC
- [ ] Приоритеты P0/P1 на спринт
- [ ] UAT-результаты
- [ ] Решение по change requests

### Что PM отдаёт **Sales**

- [ ] Case study / цитаты
- [ ] KPI fact для КП
- [ ] Fit assessment следующих лидов

---

## 13. Связанные документы

| Документ | Когда использовать |
|----------|-------------------|
| [`MVP-TZ.md`](MVP-TZ.md) | **ТЗ MVP** — scope, flows, приёмка (читать первым) |
| [`notion/PRODUCT-PLAN.md`](notion/PRODUCT-PLAN.md) | Стратегия, MVP, RICE |
| [`notion/NOTION-SETUP.md`](notion/NOTION-SETUP.md) | Настройка workspace |
| [`PRD.md`](PRD.md) | Требования, агенты |
| [`FIRST-MEETING-GUIDE.md`](FIRST-MEETING-GUIDE.md) | Discovery-встречи |
| [`SALES-PLAYBOOK-RU.md`](SALES-PLAYBOOK-RU.md) | Воронка, ICP, офферы |
| [`IMPLEMENTATION_GUIDE.md`](../IMPLEMENTATION_GUIDE.md) | Onboarding клиента (eng-facing) |
| [`ROSDORMONITORING-INTEGRATION.md`](ROSDORMONITORING-INTEGRATION.md) | Permit / Росдор |
| [`meeting-protocol-template.md`](meeting-protocol-template.md) | Протоколы |
| [`backlog-12-weeks.md`](backlog-12-weeks.md) | Dev backlog FP-1…FP-N |
| [`apps/README.md`](../../apps/README.md) | API endpoints, demo login |

---

## Приложение A — 90-дневный календарь PM (пилот 6 ТС)

| Нед | Фаза | Ключевые задачи PM |
|-----|------|-------------------|
| 0 | Подготовка | Notion, demo, sync eng |
| 1 | Discovery | Встреча, протокол, BANT |
| 2 | Scope | One-pager, KPI baseline, backlog prio |
| 3 | Контракт | NDA, доступы, kickoff |
| 4 | Пилот W1 | Milestone Wialon; weekly #1 |
| 5 | Пилот W2 | Milestone ТМ; weekly #2 |
| 6 | Пилот W3 | Permit 3/5; weekly #3 |
| 7 | Пилот W4 | ROI dashboard; weekly #4 |
| 8 | Пилот W5 | Fuel + 1С; weekly #5 |
| 9 | Пилот W6 | Обучение; weekly #6 |
| 10 | Приёмка | Отчёт, встреча ЛПР |
| 11 | Paid | КП, контракт |
| 12 | Handoff | CS, roadmap Q2 |

---

## Приложение B — Шаблон карточки фичи (копировать в Notion)

```markdown
## Problem
…

## User Story
Как [роль], я хочу [что], чтобы [результат].

## Acceptance Criteria
- [ ] …
- [ ] …

## Metrics
Baseline: … | Target: …

## Dependencies
Integration: … | Blocks: …

## Discovery
→ DIS-…
```

---

*FleetPilot PM Playbook · v1.0 · Вопросы: обновляйте этот doc по итогам каждого пилота.*
