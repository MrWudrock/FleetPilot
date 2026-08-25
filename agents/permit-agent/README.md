# Permit Agent

**Permit Agent** — пятый ИИ-агент FleetPilot для автоматизации **оформления спецразрешений** на перевозку негабаритных и тяжеловесных грузов с интеграцией **Росдормониторинг**.

## Возможности

- Анализ маршрута А→Б с учётом габаритов, массы, нагрузки на оси
- Проверка необходимости ПОДД и особых условий движения
- Интеграция с реестром разрешений (parser API / Росдормониторинг)
- AI-объяснение для диспетчера (human-in-the-loop)
- Черновики документов (ПОДД, компенсация) — фаза 2+

## Pipeline

```
Заявка (габариты, А→Б, ТС)
  → Route analysis (Росдормониторинг / OSRM)
  → Legal check (RAG: 257-ФЗ, ПП №12)
  → Risk score + альтернативные маршруты
  → Диспетчер утверждает → подача
```

## Интеграции

| Система | URL | Фаза |
|---------|-----|------|
| Реестр разрешений | urd.safe-route.ru | 1 |
| ЛК перевозчика | urm.safe-route.ru | 2 (Playwright) |
| Parser API | parser-api.com (опционально) | 1 |

## Документация

- [`docs/fleet-ai/ROSDORMONITORING-INTEGRATION.md`](../../docs/fleet-ai/ROSDORMONITORING-INTEGRATION.md)
- [`docs/fleet-ai/FIRST-MEETING-GUIDE.md`](../../docs/fleet-ai/FIRST-MEETING-GUIDE.md)

## Конфигурация

См. `config.yaml` — пороги габаритов, LLM cascade, API keys.

## Статус

🟢 **Sprint 7** — API runtime (`/api/v1/agents/permit/*`, `/api/v1/integrations/rosdor/*`).  
Rule-based анализ маршрута + audit log. LLM/RAG и live parser API — Sprint 7.1+.
