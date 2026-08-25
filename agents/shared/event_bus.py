# Event Bus

Шина событий для межагентного взаимодействия.

## Описание

Event Bus обеспечивает асинхронное взаимодействие между агентами и модулями FleetPilot.

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Route Agent │────▶│             │────▶│  Consumers  │
└─────────────┘     │             │     └─────────────┘
┌─────────────┐     │  Event Bus  │     ┌─────────────┐
│Dispatch Agent│───▶│  (Redis)    │────▶│  Analytics  │
└─────────────┘     │             │     └─────────────┘
┌─────────────┐     │             │     ┌─────────────┐
│ Fuel Agent  │────▶│             │────▶│   Alerts    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Типы событий

### GPS и ТС

| Событие | Описание | Источник |
|---------|----------|----------|
| `vehicle.position_updated` | Обновление позиции ТС | GPS |
| `vehicle.status_changed` | Изменение статуса ТС | GPS |
| `vehicle.fuel_changed` | Изменение уровня топлива | ДУТ |
| `vehicle.dtc_detected` | Обнаружен DTC-код | CAN |

### Заявки и маршруты

| Событие | Описание | Источник |
|---------|----------|----------|
| `order.created` | Новая заявка | Dispatch |
| `order.classified` | Заявка классифицирована | Dispatch |
| `order.assigned` | Заявка назначена | Dispatch |
| `route.optimized` | Маршрут оптимизирован | Route |
| `route.approved` | Маршрут утверждён | Dispatcher |
| `route.deviation` | Отклонение от маршрута | Route |

### Топливо

| Событие | Описание | Источник |
|---------|----------|----------|
| `fuel.drain_detected` | Обнаружен слив | Fuel |
| `fuel.anomaly_detected` | Аномалия расхода | Fuel |
| `fuel.refuel_detected` | Обнаружена заправка | Fuel |
| `fuel.monthly_report` | Месячный отчёт готов | Fuel |

### ТО

| Событие | Описание | Источник |
|---------|----------|----------|
| `maintenance.scheduled` | ТО запланировано | Maintenance |
| `maintenance预警` | Предупреждение о ТО | Maintenance |
| `maintenance.completed` | ТО завершено | Maintenance |

## Формат события

```json
{
  "event_id": "uuid",
  "event_type": "vehicle.fuel_changed",
  "timestamp": "2026-06-21T14:30:00Z",
  "source": "fuel-agent",
  "organization_id": "org_123",
  "vehicle_id": "vh_001",
  "payload": {
    "previous_level": 75.2,
    "current_level": 62.1,
    "delta_liters": -47.0,
    "time_delta_min": 12,
    "location": {"lat": 55.75, "lon": 37.62},
    "confidence": 0.92
  },
  "metadata": {
    "agent_version": "1.0",
    "processing_time_ms": 150
  }
}
```

## Подписка на события

```python
# Подписка на конкретное событие
@event_bus.subscribe("fuel.drain_detected")
async def handle_drain(event):
    if event.payload["confidence"] >= 0.85:
        await alerting.send_alert(
            severity="high",
            title=f"Обнаружен слив: {event.vehicle_id}",
            body=f"−{event.payload['delta_liters']} л за {event.payload['time_delta_min']} мин",
            recipients=["fleet_manager"]
        )

# Подписка на группу событий
@event_bus.subscribe("vehicle.*")
async def handle_vehicle_events(event):
    await analytics.track(event)
```

## Гарантии доставки

- **At-least-once:** события сохраняются в Redis Stream
- **Retry:** 3 попытки с экспоненциальной задержкой
- **DLQ:** неудачные события в Dead Letter Queue
- **Retention:** 7 дней для Redis Stream
