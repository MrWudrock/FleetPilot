# Импорт backlog FleetPilot в Jira — пошагово

**Файл для импорта:** [`backlog-jira-import.csv`](backlog-jira-import.csv)  
**Задач:** 65 (10 Epics + 55 Stories/Tasks)  
**Нужны права:** администратор Jira Cloud (для CSV-импорта через System)

---

## Часть 0. Подготовка (один раз, ~15 мин)

### Шаг 0.1 — Создать проект

1. Откройте Jira: `https://ВАШ-ДОМЕН.atlassian.net`
2. В левом верхнем углу нажмите **Create** (или **+** → **Project**)
3. Выберите шаблон **Scrum** (рекомендуется) или **Kanban**
4. Нажмите **Use template**
5. Заполните:
   - **Name:** `FleetPilot`
   - **Key:** `FP` (или `FLEET`)
6. Нажмите **Create project**

### Шаг 0.2 — Убедиться, что есть типы задач Epic / Story / Task

1. Откройте проект **FleetPilot**
2. Слева внизу: **Project settings** (⚙ рядом с названием проекта)
3. В меню слева: **Issue types**
4. Проверьте, что в списке есть **Epic**, **Story**, **Task**  
   *(В Scrum-шаблоне они уже есть.)*

### Шаг 0.3 — Включить Story Points

1. **Project settings** → **Fields**
2. Найдите поле **Story point estimate** (или **Story Points**)
3. Если его нет на экране задачи:
   - Перейдите в **Jira settings** (шестерёнка ⚙ **глобально**, не проекта) → **Issues** → **Screens**
   - Откройте экран вашего проекта (например *Default Scrum Issue Screen*)
   - **Configure** → перетащите **Story point estimate** на экран → **Save**

### Шаг 0.4 — Создать 6 спринтов на доске

1. Откройте проект → вкладка **Backlog** (слева)
2. Справа от надписи **Backlog** найдите **Create sprint** (или кнопку **+** у блока Sprints)
3. Создайте по одному спринту с **точными** именами (как в CSV):

| № | Имя спринта (копировать как есть) |
|---|-------------------------------------|
| 1 | `Sprint 1 — Foundation` |
| 2 | `Sprint 2 — Integrations` |
| 3 | `Sprint 3 — Fleet Map` |
| 4 | `Sprint 4 — Fuel Agent` |
| 5 | `Sprint 5 — Route Agent` |
| 6 | `Sprint 6 — Launch` |

4. Даты спринтов задайте по своему календарю (по 2 недели каждый)
5. **Start** первый спринт не обязательно — можно после импорта

---

## Часть 1. Импорт CSV (админ Jira Cloud)

> Если пункта **External system import** нет — у вашего аккаунта нет прав админа. Попросите админа или используйте **Часть 3** (ручной перенос через Backlog).

### Шаг 1.1 — Открыть импорт

**Путь A (классический Jira Cloud):**

1. Нажмите **⚙ Jira settings** (шестерёнка) **в правом верхнем углу** — не «Project settings», а **глобальные** настройки Jira
2. В левой колонке: **System**
3. Прокрутите до блока **IMPORT AND EXPORT**
4. Нажмите **External system import**
5. Нажмите **CSV**

**Путь B (новый Atlassian Admin):**

1. Откройте [admin.atlassian.com](https://admin.atlassian.com)
2. **Products** → **Jira** → ваш сайт
3. **Import** / **Migrate** → **CSV**

**Путь C (импорт в конкретный проект — если доступен на вашем плане):**

1. **FleetPilot** → **Project settings** → **Import** (или **External import**)

### Шаг 1.2 — Загрузить файл

1. Нажмите **Select CSV file** / **Browse**
2. Выберите файл с диска:

   ```
   C:\Users\Wu\develop\startapp log\docs\fleet-ai\backlog-jira-import.csv
   ```

3. Кодировка: **UTF-8**
4. Разделитель: **Comma** (запятая)
5. **Next** / **Continue**

### Шаг 1.3 — Выбрать проект назначения

1. **Project:** выберите **FleetPilot** (ключ FP)
2. **Next**

### Шаг 1.4 — Сопоставить колонки CSV с полями Jira

На экране **Map fields** сопоставьте **каждую** колонку CSV:

| Колонка в CSV | Поле в Jira | Обязательно |
|---------------|-------------|-------------|
| Summary | **Summary** | ✓ |
| Issue Type | **Issue Type** | ✓ |
| Description | **Description** | ✓ |
| Priority | **Priority** | ✓ |
| Labels | **Labels** | ✓ |
| Story Points | **Story point estimate** | ✓ |
| Epic Name | **Epic Name** *(для Epic)* или **Parent** / **Epic Link** *(для Story/Task)* | ✓ |
| Sprint | **Sprint** | желательно |
| External ID | *не импортировать* или custom field | опционально |
| Component | **Component/s** | опционально |
| ~~Fix Version~~ | **не импортировать** | см. DT001 ниже |

**Важно про Epic Name:**

- Для строк с **Issue Type = Epic** → маппинг на **Epic Name**
- Для **Story** и **Task** → маппинг на **Epic Link** (или **Parent**, если Jira предлагает только его)

Если **Sprint** не находится в списке полей — пропустите; назначите спринты вручную в **Части 2**.

### Шаг 1.5 — Проверить превью и запустить

1. Просмотрите **первые 5–10 строк** превью:
   - Epics: `EP-1 Platform & Auth`, `EP-2 Integration Hub`, …
   - Tasks: `FP-1 Monorepo setup`, …
2. Нажмите **Begin Import** / **Import**
3. Дождитесь завершения (обычно 1–3 мин на 65 задач)
4. Откройте отчёт импорта — проверьте **0 errors** или исправьте ошибки

---

## Часть 2. После импорта (~10 мин)

### Шаг 2.1 — Проверить Epics

1. Проект **FleetPilot** → **Backlog**
2. Слева панель **Epics** (или вкладка **Epics**)
3. Должно быть **10 эпиков:** EP-1 … EP-10

### Шаг 2.2 — Привязать задачи к эпикам (если Epic Link пустой)

1. **Backlog** → **Issues** (список всех задач)
2. Фильтр: `project = FP AND type != Epic`
3. Выделите задачи одного спринта (Ctrl+click)
4. **⋯** (три точки) → **Bulk change**
5. **Edit issues** → **Epic Link** (или **Parent**)
6. Выберите эпик, например `EP-1 Platform & Auth`
7. **Confirm**

Повторите для каждого эпика или используйте фильтр по **Sprint**.

### Шаг 2.3 — Разложить задачи по спринтам (если Sprint не импортировался)

1. **Backlog**
2. В блоке **Backlog** (верхний список) — все импортированные задачи
3. **Перетащите мышью** задачи в нужный спринт:

| Спринт | Задачи (префикс ID) |
|--------|---------------------|
| Sprint 1 — Foundation | FP-1 … FP-8 |
| Sprint 2 — Integrations | FP-10 … FP-18 |
| Sprint 3 — Fleet Map | FP-20 … FP-28 |
| Sprint 4 — Fuel Agent | FP-30 … FP-37 |
| Sprint 5 — Route Agent | FP-40 … FP-47 |
| Sprint 6 — Launch | FP-50 … FP-65 |

### Шаг 2.4 — Создать доску и проверить колонки

1. **Board** (вкладка слева)
2. Убедитесь, что колонки: *To Do* → *In Progress* → *Done*
3. **Start sprint** для Sprint 1, если готовы к работе

### Шаг 2.5 — Фильтр для всего backlog

1. **Filters** → **Create filter**
2. JQL:
   ```jql
   project = FP ORDER BY rank ASC
   ```
3. Сохраните как **FleetPilot MVP Backlog**

---

## Часть 3. Если CSV-импорт недоступен (нет прав админа)

### Вариант A — Попросить админа

Отправьте админу файл `backlog-jira-import.csv` и ссылку на этот документ.

### Вариант B — Импорт только Epics вручную + копирование

1. **Create** → **Epic** — создайте 10 эпиков вручную (имена из CSV, колонка Summary)
2. Для каждой задачи: **Create** → **Story** / **Task** → заполните Summary, Story Points, Epic Link

### Вариант C — Приложение «CSV Import for Jira»

1. **⚙ Jira settings** → **Apps** → **Explore apps** (Marketplace)
2. Найдите **CSV Import** (Atlassian или сторонние)
3. Установите → импорт из того же CSV в проект FleetPilot

---

## Сопоставление типов и приоритетов

| CSV Issue Type | Jira |
|----------------|------|
| Epic | Epic |
| Story | Story |
| Task | Task |

| CSV Priority | Jira |
|--------------|------|
| High | High |
| Medium | Medium |
| Low | Low |

---

## Labels (создадутся автоматически)

`mvp`, `epic`, `p0`, `p1`, `frontend`, `backend`, `ai`, `infra`, `integrations`, `design`

---

## Частые ошибки

### DT001 — `Locale and date and time values don't match` + `MVP v1.0`

**Причина:** колонка **Fix Version** со значением `MVP v1.0` была сопоставлена с **полем даты** (Due date, Start date и т.п.), а не с **Fix version/s**. Jira пытается прочитать `MVP v1.0` как дату и падает на всех 65 строках.

**Решение (выберите одно):**

1. **Рекомендуется:** используйте обновлённый CSV **без колонки Fix Version**  
   `docs/fleet-ai/backlog-jira-import.csv` (уже исправлен)
2. На экране **Map fields** → колонку Fix Version **не сопоставляйте** или сопоставьте только с **Fix version/s** (не с Date!)
3. Сначала создайте версию в Jira: **Project settings → Versions → Create** → имя `MVP-1`, затем импортируйте без этой колонки и назначьте версию через Bulk change

| Проблема | Что сделать |
|----------|-------------|
| **Story Points = пусто** | Project settings → Screens → добавить поле Story point estimate |
| **Epic Link не заполнился** | Bulk change → Epic Link вручную (шаг 2.2) |
| **Sprint не импортировался** | Drag-and-drop на Backlog (шаг 2.3) |
| **Duplicate issues** | Удалите дубликаты: Issue → **⋯** → **Delete**; перед повторным импортом очистите проект |
| **Issue Type "Epic" not found** | Используйте Scrum-шаблон или добавьте Epic в Project settings → Issue types |
| **Кракозябры в описании** | При импорте выберите кодировку **UTF-8** |

---

## Быстрая проверка «всё на месте»

- [ ] 10 Epics (EP-1 … EP-10)
- [ ] 55 дочерних задач (FP-1 … FP-65, без пропусков)
- [ ] У каждой Story/Task есть Epic Link
- [ ] Story Points заполнены (3, 5, 8 …)
- [ ] 6 спринтов на Backlog с задачами внутри
- [ ] Labels: `mvp`, `p0` на P0-задачах

---

*FleetPilot · backlog-jira-import.csv · v1.0 · 21.06.2026*
