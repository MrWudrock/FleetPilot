# FleetPilot — данные для KPI Dashboard

**Версия:** 1.0 · **Дата:** 22.06.2026  
**Экран:** Wireframe 01 · ROI Dashboard

---

## 1. Карточки KPI на dashboard

| KPI (UI) | Источник данных | Таблица / агент | Статус MVP |
|----------|-----------------|-----------------|------------|
| **Экономия за месяц** | Сумма экономии по агентам за текущий месяц | `savings_entries` | ✅ Demo seed / Sprint 4+ live |
| **ТС в автопарке** | Количество ТС организации | `vehicles` | ✅ Реальные данные |
| **Активных маршрутов** | Заявки в статусе assigned / in_transit | `orders` | ✅ Demo seed / Sprint 5+ Route Agent |
| **Топливные алерты** | Неподтверждённые алерты Fuel Agent | `fuel_alerts` | ✅ Demo seed / Sprint 4 Fuel Agent |
| **ROI за 12 мес.** | Расчёт: `(годовая экономия / годовая подписка) × 100` | `savings_entries` + тариф | ✅ Расчётный |
| **Экономия Permit Agent** | Время на спецразрешение × ставка специалиста | `savings_entries.category=permit` | Sprint 7+ |

### Дополнительные метрики (wireframe, API готово)

| Метрика | Поле API | Источник |
|---------|----------|----------|
| Заявок сегодня | `orders_today` | `orders.created_at` за сегодня |
| Критические алерты | `fuel_alerts_critical` | `fuel_alerts.severity = critical` |
| Δ экономии vs прошлый мес. | `monthly_savings_delta_pct` | `savings_entries` текущий / прошлый месяц |
| Окупаемость | `payback_months` | Подписка ₽49K / месячная экономия |
| Разбивка по агентам | `breakdown.*` | `savings_entries.category` |

---

## 2. Детализация по агентам

### Fuel Agent → экономия + алерты

| Поле | Что нужно | Откуда берётся (production) |
|------|-----------|----------------------------|
| `breakdown.fuel` | ₽ экономии на топливе/мес | Fuel Agent: baseline consumption vs факт (ДУТ Omnicomm) |
| `fuel_alerts_count` | Число алертов | `fuel_level` stream + anomaly detection (confidence ≥ 0.85) |
| `fuel_alerts_critical` | Сливы / критические | Внезапное падение уровня > порога, вне АЗС |

**Входные данные:**
- Omnicomm API: `fuel_level_percent`, `fuel_level_liters`, GPS
- CAN-шина (опционально): мгновенный расход
- Baseline: скользящее среднее л/100км по каждому ТС

### Route Agent → экономия + маршруты

| Поле | Что нужно | Откуда |
|------|-----------|--------|
| `breakdown.route` | ₽ экономии на маршрутах | OR-Tools VRP: км/топливо до vs после оптимизации |
| `active_routes_count` | Активные рейсы | `orders` / `route_plans` в статусе in_transit |

**Входные данные:**
- Yandex Maps Matrix API + traffic
- Позиции ТС (`vehicle_telemetry`)
- Заявки с точками доставки

### Dispatch Agent → экономия + заявки

| Поле | Что нужно | Откуда |
|------|-----------|--------|
| `breakdown.dispatch` | ₽ экономии диспетчеризации | Время диспетчера × ставка (baseline 2.8 ч → 0.4 ч) |
| `orders_today` | Заявок за день | TMS / email / Excel import → `orders` |

**Входные данные:**
- Заявки (email, Excel, Master TMS API)
- Доступность водителей и ТС
- SLA клиентов

### Maintenance Agent → экономия

| Field | Что нужно | Откуда |
|-------|-----------|--------|
| `breakdown.maintenance` | ₽ снижения простоев | Предиктивное ТО vs внеплановый ремонт |

**Входные данные:**
- Пробег (`odometer`), моточасы
- DTC-коды CAN
- История ТО

---

## 3. Формулы расчёта

```
monthly_savings_rub = SUM(savings_entries.amount_rub) WHERE period_month = текущий месяц

annual_savings_rub  = monthly_savings_rub × 12

roi_percent_annual  = (annual_savings_rub / (49_000 × 12)) × 100

payback_months      = (49_000 × 12) / annual_savings_rub

monthly_savings_delta_pct = ((текущий − прошлый) / прошлый) × 100
```

**Тариф по умолчанию:** ₽49 000/мес (Founding offer, до 30 ТС).

---

## 4. Demo seed (FP-7)

Команда:

```powershell
docker compose exec api python scripts/seed_demo.py
# или --force для пересоздания
```

| Параметр | Значение |
|----------|----------|
| Org | Демо Автопарк (`demo-fleet`) |
| Login | `demo@fleetpilot.ru` / `Demo12345!` |
| ТС | 32 (28 active, 2 maintenance, 2 inactive) |
| Экономия/мес | ₽267 000 (fuel 142K + route 85K + dispatch 25K + maintenance 15K) |
| Алерты | 3 (1 critical) |
| Заявки сегодня | 18 (5 active routes) |
| Интеграция | Omnicomm (active, demo) |

---

## 5. Roadmap: переход с demo на live data

| Sprint | Что подключается | KPI становятся live |
|--------|------------------|---------------------|
| S2 | Omnicomm sync | `vehicles.external_ids`, GPS online |
| S4 | Fuel Agent | `fuel_alerts`, `breakdown.fuel` |
| S5 | Route Agent | `active_routes`, `breakdown.route` |
| S6 | Dispatch Agent | `orders_today`, `breakdown.dispatch` |
| S7+ | Maintenance Agent | `breakdown.maintenance` |

---

## 6. API

```
GET /api/v1/analytics/roi
Authorization: Bearer <token>
```

Ответ: `RoiKpiResponse` — все поля dashboard + `breakdown` + `data_sources`.

---

*FleetPilot · KPI Data Spec · v1.0*
