# Alerting System

Система алертов FleetPilot.

## Описание

Централизованная система отправки уведомлений с поддержкой нескольких каналов и эскалации.

## Уровни серьёзности

| Уровень | Описание | Время реакции | Каналы |
|---------|----------|---------------|--------|
| `critical` | Критический инцидент | Немедленно | SMS + Email + Push + Webhook |
| `high` | Высокий приоритет | < 1 часа | Email + Push |
| `medium` | Средний приоритет | < 24 часов | Email |
| `low` | Информационный | В отчёте | Email (дайджест) |

## Типы алертов

### Fuel Agent

| Алерт | Серьёзность | Условие |
|-------|-------------|---------|
| Слив топлива | `critical` | confidence ≥ 0.95 |
| Подозрительный слив | `high` | confidence ≥ 0.85 |
| Заправка вне маршрута | `medium` | confidence ≥ 0.70 |
| Превышение расхода | `low` | > 20% vs baseline |

### Route Agent

| Алерт | Серьёзность | Условие |
|-------|-------------|---------|
| Критическое отклонение | `high` | > 15 км от маршрута |
| Задержка доставки | `medium` | > 30 мин опоздания |
| Пробка на маршруте | `low` | задержка > 20 мин |

### Dispatch Agent

| Алерт | Серьёзность | Условие |
|-------|-------------|---------|
| Нет доступных ТС | `high` | 0 подходящих ТС |
| Истекает SLA | `medium` | < 2 часа до дедлайна |

### Maintenance Agent

| Алерт | Серьёзность | Условие |
|-------|-------------|---------|
| Критическое ТО | `critical` | < 7 дней или DTC P0300 |
| Требуется ТО | `high` | < 14 дней |
| Плановое ТО | `medium` | < 30 дней |

## Формат алерта

```json
{
  "alert_id": "uuid",
  "severity": "high",
  "source": "fuel-agent",
  "organization_id": "org_123",
  "title": "Подозрительный слив: КАМАЗ А123БВ777",
  "body": "−47 л за 12 мин. Confidence: 92%. Водитель: Иванов С.",
  "vehicle_id": "vh_001",
  "event_id": "evt_123",
  "actions": [
    {"label": "Расследовать", "url": "/alerts/evt_123"},
    {"label": "Игнорировать", "action": "dismiss"}
  ],
  "created_at": "2026-06-21T14:30:00Z",
  "acknowledged_at": null,
  "resolved_at": null
}
```

## Каналы доставки

### Email

```yaml
email:
  enabled: true
  smtp_host: "${SMTP_HOST}"
  smtp_port: 587
  smtp_user: "${SMTP_USER}"
  smtp_password: "${SMTP_PASSWORD}"
  from: "FleetPilot <alerts@fleetpilot.ru>"
  templates:
    critical: "alert_critical.html"
    high: "alert_high.html"
    medium: "alert_medium.html"
    low: "alert_low.html"
```

### SMS

```yaml
sms:
  enabled: false
  provider: smsc
  api_key: "${SMSC_API_KEY}"
  sender: "FleetPilot"
```

### Push (Web)

```yaml
push:
  enabled: true
  method: websocket
  channel: "org_{organization_id}"
```

### Webhook

```yaml
webhook:
  enabled: false
  url: "${ALERT_WEBHOOK_URL}"
  method: POST
  headers:
    Authorization: "Bearer ${ALERT_WEBHOOK_TOKEN}"
  retry_count: 3
  timeout_ms: 5000
```

## Эскалация

```yaml
escalation:
  rules:
    - severity: critical
      timeout_min: 15
      escalate_to: [fleet_manager, ceo]
    - severity: high
      timeout_min: 60
      escalate_to: [fleet_manager]
    - severity: medium
      timeout_min: 1440  # 24 часа
      escalate_to: [dispatcher]
```

## Дайджест

Ежедневный дайджест для `low` и `medium` алертов:

```yaml
digest:
  enabled: true
  schedule: "0 9 * * *"  # Каждый день в 9:00
  recipients: [fleet_manager]
  include:
    - low_alerts_count
    - medium_alerts_count
    - top_3_alerts
    - resolved_alerts
```

## Метрики

```python
# Отслеживание эффективности алертов
metrics = {
    "alerts_total": Counter("alerts_total", ["severity", "source"]),
    "alerts_resolved": Counter("alerts_resolved", ["severity"]),
    "alerts_resolution_time": Histogram("alerts_resolution_time_seconds"),
    "false_positive_rate": Gauge("alerts_false_positive_rate"),
}
```
