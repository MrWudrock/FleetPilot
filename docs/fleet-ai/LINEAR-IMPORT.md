# Импорт backlog в Linear через API

**Скрипт:** [`scripts/linear_import.py`](../../scripts/linear_import.py)  
**CSV:** [`backlog-linear-import.csv`](backlog-linear-import.csv) · 68 issues (10 epics + 58 tasks)

---

## Могу ли я импортировать за вас?

**Да**, через Linear GraphQL API — но нужен **ваш Personal API key**.  
Сейчас ключ в окружении **не задан**, поэтому импорт нужно запустить у вас локально (или передать ключ в переменной окружения для одного запуска).

> Не публикуйте API key в чатах и не коммитьте в git.

---

## Шаг 1. Получить API key

1. [linear.app](https://linear.app) → аватар → **Settings**
2. **Account** → **Security & access** → **Personal API keys**
3. **Create key** → скопируйте `lin_api_...`

---

## Шаг 2. Узнать Team ID (опционально)

Если в workspace одна команда — скрипт выберет её сам.

Иначе:

```powershell
$env:LINEAR_API_KEY = "lin_api_ВАШ_КЛЮЧ"
python -c "
import json, os, urllib.request
req = urllib.request.Request('https://api.linear.app/graphql',
  data=json.dumps({'query': '{ teams { nodes { id key name } } }'}).encode(),
  headers={'Authorization': os.environ['LINEAR_API_KEY'], 'Content-Type': 'application/json'})
print(json.loads(urllib.request.urlopen(req).read())['data']['teams']['nodes'])
"
```

Сохраните `id` или `key` (например `ENG`):

```powershell
$env:LINEAR_TEAM_ID = "ENG"
```

---

## Шаг 3. Dry-run (без записи)

```powershell
cd "C:\Users\Wu\develop\startapp log"
python scripts/linear_import.py --dry-run
```

---

## Шаг 4. Импорт

```powershell
cd "C:\Users\Wu\develop\startapp log"
$env:LINEAR_API_KEY = "lin_api_ВАШ_КЛЮЧ"
# $env:LINEAR_TEAM_ID = "ENG"   # если несколько команд
python scripts/linear_import.py
```

Скрипт автоматически:

1. Создаёт проект **FleetPilot** (если нет)
2. Создаёт 6 **milestones** (Sprint 1–6)
3. Создаёт **10 epics** как parent issues
4. Создаёт **58 задач** с `parentId`, labels, estimate, priority

---

## Альтернатива без API — CSV import в UI

Linear → **Settings** → **Workspace** → **Import** → **CSV**  
Файл: `docs/fleet-ai/backlog-linear-import.csv`

---

## Troubleshooting

| Ошибка | Решение |
|--------|---------|
| `401 Unauthorized` | Неверный или отозванный API key |
| `Set LINEAR_TEAM_ID` | Несколько команд — укажите team id/key |
| Duplicate issues | Повторный запуск создаст дубликаты; удалите в Linear или используйте новый проект |
| Rate limit | Скрипт делает паузу 0.2s между issues; при ошибке повторите позже |

---

*FleetPilot · Linear import · v1.0*
