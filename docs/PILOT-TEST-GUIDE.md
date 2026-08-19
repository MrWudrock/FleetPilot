# Проверка полного demo-функционала (карта, Wialon, ТМ, Fuel, Permit)

## Подготовка

```powershell
cd "C:\Users\Wu\develop\startapp log"
docker compose up -d postgres redis api
.\seed-demo.ps1   # или: docker compose exec api env PYTHONPATH=/app python scripts/seed_demo.py --force
cd apps\web
$env:NEXT_PUBLIC_API_URL="http://localhost:8800"
npm run dev
```

Логин: `demo@fleetpilot.ru` / `Demo12345!`

---

## Что открыть в UI

| Экран | URL | Что проверить |
|-------|-----|----------------|
| ROI | `/dashboard` | KPI ₽267K, 32 ТС |
| **Карта** | `/map` | Маркеры на OSM, фильтры motion, **Sync Wialon** |
| **Топливо** | `/fuel` | 3 алерта, **Acknowledge** |
| **Диспетчеризация** | `/dispatch` | Заявки ТМ, создать заявку, назначить ТС, **Sync ТМ** |
| **Permit** | `/pilot` | Анализ маршрута, утверждение, Росдор DEMO |
| **Интеграции** | `/integrations` | Подключить Wialon / ТМ, sync |

---

## Сценарий пилотного теста (15 мин)

1. **Интеграции** → Подключить Wialon + Sync позиции  
2. **Карта** → увидеть ТС, сменить фильтр `moving` / `offline`  
3. **Интеграции** → Подключить ТрансМенеджер + Sync заявки  
4. **Диспетчеризация** → создать заявку Москва→Казань → назначить ТС  
5. **Топливо** → подтвердить critical-алерт  
6. **Пилот · Permit** → анализ негабарита → Утвердить → check `DEMO-12345`

---

## API (Swagger)

http://localhost:8800/docs

Новые группы: **fleet** — `/vehicles`, `/fuel/alerts`, `/integrations/*`, `/orders`

> Режим **DEMO**: позиции и ТМ не ходят во внешние системы — эмуляция для полноценного UI-теста. Live Wialon/ТМ — следующий этап после доступов клиента.
