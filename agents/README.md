# FleetPilot Agent Templates

Шаблоны ИИ-агентов для автоматизации транспортно-логистических компаний.

## Структура

```
agents/
├── README.md                          # Этот файл
├── route-agent/
│   ├── README.md                      # Описание агента
│   ├── config.yaml                    # Конфигурация
│   ├── prompts/                       # Промпты для LLM
│   │   ├── system.md                  # Системный промпт
│   │   ├── route_optimization.md      # Оптимизация маршрута
│   │   └── deviation_explanation.md   # Объяснение отклонений
│   ├── rules/                         # Правила (без LLM)
│   │   ├── time_windows.yaml          # Временные окна
│   │   └── vehicle_constraints.yaml   # Ограничения ТС
│   └── integration/
│       ├── yandex_maps.py             # Интеграция Yandex Maps
│       └── ortools_vrp.py             # VRP solver
├── dispatch-agent/
│   ├── README.md
│   ├── config.yaml
│   ├── prompts/
│   │   ├── system.md
│   │   ├── classify_order.md          # Классификация заявки
│   │   └── assign_driver.md           # Назначение водителя
│   ├── rules/
│   │   ├── ftl_ltl_rules.yaml         # Правила FTL/LTL
│   │   └── assignment_weights.yaml    # Веса назначения
│   └── integration/
│       ├── email_parser.py            # Парсер email
│       └── excel_parser.py            # Парсер Excel
├── fuel-agent/
│   ├── README.md
│   ├── config.yaml
│   ├── prompts/
│   │   ├── system.md
│   │   ├── drain_alert.md             # Алерт слива
│   │   └── monthly_report.md          # Месячный отчёт
│   ├── rules/
│   │   ├── drain_thresholds.yaml      # Пороги слива
│   │   ├── consumption_baselines.yaml # Базовые расходы
│   │   └── driving_scores.yaml        # Рейтинги водителей
│   └── integration/
│       ├── omnicomm_api.py            # API Omnicomm
│       └── can_parser.py              # Парсер CAN-данных
├── maintenance-agent/
│   └── ...
├── permit-agent/                      # NEW: спецразрешения · Росдормониторинг
│   ├── README.md
│   ├── config.yaml
│   └── prompts/
└── shared/
    ├── vehicle_model.py               # Unified Vehicle Model
    ├── event_bus.py                   # Шина событий
    └── alerting.py                    # Система алертов
```

## Быстрый старт

1. Скопируйте шаблоны агентов в проект
2. Заполните `config.yaml` для каждого агента
3. Настройте интеграции (API ключи GPS-систем)
4. Запустите агентов через Agent Orchestrator

## Конфигурация

Каждый агент имеет:
- `config.yaml` — параметры, пороги, веса
- `prompts/` — промпты для LLM (Claude Sonnet)
- `rules/` — детерминированные правила (без LLM)
- `integration/` — модули интеграции с внешними системами
