# FleetPilot Scan

Интерактивная карта кодовой базы в духе [Foglamp Scan](https://www.foglamp.dev/scan): клиенты, API, сервисы, агенты, хранилища и интеграции на одном ELK-графе с pan/zoom.

## Быстрый старт

```powershell
cd "C:\Users\Wu\develop\startapp log"
.\scan\serve.ps1
```

Откроется http://localhost:8787 — интерактивная карта.

## Только пересобрать граф

```powershell
python scan/build_graph.py
```

Результат: `scan/data/graph.json`.

## Что на карте

| Группа | Примеры |
|--------|---------|
| **Clients** | Web, Desktop, Landing, страницы `/dashboard`, `/map` |
| **API** | auth, fleet, ops, permit, rosdor |
| **Stores** | PostgreSQL, Redis, SQLAlchemy models |
| **Agents** | route, fuel, dispatch, maintenance, permit |
| **External** | Wialon, TransManager, Rosdor |
| **Infra** | Docker Compose, CI |

## Обновление после изменений в коде

После крупных рефакторингов:

```powershell
python scan/build_graph.py
# затем F5 в браузере или кнопка «Обновить» на странице
```
