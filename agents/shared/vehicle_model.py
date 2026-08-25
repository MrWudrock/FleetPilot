# Unified Vehicle Model

Единая модель ТС для всех агентов FleetPilot.

## Описание

Unified Vehicle Model обеспечивает консистентность данных из разных GPS-систем (Omnicomm, СтавТРЭК, MSS GLONASS) в единую структуру.

## Структура данных

```yaml
VehicleState:
  # Идентификация
  vehicle_id: string          # FleetPilot internal ID
  external_ids:               # ID во внешних системах
    omnicomm: string | null
    stavtrack: string | null
    mss_glonass: string | null
    master_tms: string | null
  plate: string               # Госномер (А123БВ777)
  vin: string | null          # VIN номер

  # Характеристики
  type: enum                  # truck_tractler | truck_rigid | van | bus
  brand: string               # КАМАЗ, МАЗ, Volvo, etc.
  model: string
  year: int
  capacity_kg: float          # Грузоподъёмность (кг)
  capacity_m3: float          # Объём кузова (м³)
  length_m: float             # Длина (м)
  width_m: float              # Ширина (м)
  height_m: float             # Высота (м)

  # Текущее состояние
  lat: float                  # Широта
  lon: float                  # Долгота
  speed: float                # Скорость (км/ч)
  heading: float              # Пеленг (0-360)
  fuel_level: float | None    # Уровень топлива (%)
  fuel_liters: float | None   # Топливо (литры)
  fuel_rate: float | None     # Расход (л/100км)
  odometer: float             # Пробег (км)
  engine_hours: float         # Моточасы

  # Статус
  status: enum                # moving | idle | stopped | offline | maintenance
  ignition: bool              # Зажигание
  charging: bool | null       # Зарядка (для EV)

  # Водитель
  driver_id: string | None
  driver_name: string | None

  # Метаданные
  source: enum                # omnicomm | stavtrack | mss_glonass
  last_update: datetime       # Время последнего обновления
  data_age_sec: int           # Возраст данных (сек)

  # ТО и состояние
  next_maintenance: date | null
  maintenance_type: string | null
  dtc_codes: list[string]     # Активные DTC-коды

  # Метрики
  fuel_efficiency: float | None  # л/100км (скользящее среднее)
  driver_score: int | null       # Рейтинг водителя (0-100)
```

## Маппинг из разных систем

### Omnicomm → Unified

```python
def map_omnicomm(vehicle_data):
    return VehicleState(
        vehicle_id=generate_id(vehicle_data['unit_id']),
        external_ids={"omnicomm": vehicle_data['unit_id']},
        plate=vehicle_data['plate_number'],
        lat=vehicle_data['latitude'],
        lon=vehicle_data['longitude'],
        speed=vehicle_data['speed'],
        fuel_level=vehicle_data['fuel_level_percent'],
        fuel_liters=vehicle_data['fuel_level_liters'],
        odometer=vehicle_data['odometer'],
        engine_hours=vehicle_data['engine_hours'],
        status=map_status(vehicle_data['movement_state']),
        source="omnicomm",
        last_update=vehicle_data['timestamp']
    )
```

### СтавТРЭК → Unified

```python
def map_stavtrack(vehicle_data):
    return VehicleState(
        vehicle_id=generate_id(vehicle_data['device_id']),
        external_ids={"stavtrack": vehicle_data['device_id']},
        plate=vehicle_data['call_sign'],
        lat=vehicle_data['lat'],
        lon=vehicle_data['lon'],
        speed=vehicle_data['speed'],
        odometer=vehicle_data['mileage'],
        status=map_status(vehicle_data['state']),
        source="stavtrack",
        last_update=vehicle_data['time']
    )
```

## Синхронизация

- **Частота:** каждые 30 сек (Omnicomm), 60 сек (СтавТРЭК)
- **Fallback:** если нет обновлений > 5 мин → статус `offline`
- **Кэширование:** Redis с TTL 60 сек
- **Хранение:** TimescaleDB для телеметрии, PostgreSQL для состояний

## Использование в агентах

```python
# Получение текущего состояния всех ТС
vehicles = await vehicle_model.get_all(organization_id="org_123")

# Фильтрация по статусу
moving = [v for v in vehicles if v.status == "moving"]

# Фильтрация по местоположению
nearby = vehicle_model.find_nearby(
    lat=55.75, lon=37.62,
    radius_km=50,
    status="idle"
)
```
