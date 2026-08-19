"""Rule-based permit analysis (Sprint 7 — без LLM)."""

from app.models.enums import PermitRiskLevel
from app.schemas.permit import CargoSpec, PermitAnalysisResult, RoutePoint

STANDARD_LIMITS_M = {
    "width_m": 2.55,
    "height_m": 4.0,
    "length_m": 12.0,
}

LEGAL_REFERENCES = [
    "257-ФЗ «О дорогах и дорожной деятельности»",
    "Постановление Правительства РФ № 12 от 16.01.2021",
    "КоАП РФ ст. 12.21.1 (негабарит)",
]


def _point_label(point: RoutePoint) -> str:
    if point.name:
        return point.name
    if point.address:
        return point.address
    if point.lat is not None and point.lon is not None:
        return f"{point.lat:.4f}, {point.lon:.4f}"
    return "точка маршрута"


def analyze_route_rules(
    origin: RoutePoint,
    destination: RoutePoint,
    cargo: CargoSpec,
    *,
    waypoints: list[RoutePoint] | None = None,
) -> PermitAnalysisResult:
    waypoints = waypoints or []
    exceeds = {
        "width": cargo.width_m > STANDARD_LIMITS_M["width_m"],
        "height": cargo.height_m > STANDARD_LIMITS_M["height_m"],
        "length": cargo.length_m > STANDARD_LIMITS_M["length_m"],
    }
    permit_required = any(exceeds.values()) or cargo.mass_kg > 44_000

    max_axle = max(cargo.axle_loads_kg) if cargo.axle_loads_kg else 0.0
    heavy_axle = max_axle > 10_000
    podd_required = exceeds["width"] or exceeds["height"] or heavy_axle

    oversize_score = sum(
        [
            max(0.0, cargo.width_m / STANDARD_LIMITS_M["width_m"] - 1),
            max(0.0, cargo.height_m / STANDARD_LIMITS_M["height_m"] - 1),
            max(0.0, cargo.length_m / STANDARD_LIMITS_M["length_m"] - 1),
        ]
    )
    mass_score = max(0.0, cargo.mass_kg / 44_000 - 1)
    risk_score = min(1.0, 0.35 + oversize_score * 0.25 + mass_score * 0.2 + (0.15 if heavy_axle else 0))

    if risk_score >= 0.75:
        risk_level = PermitRiskLevel.HIGH
    elif risk_score >= 0.45:
        risk_level = PermitRiskLevel.MEDIUM
    else:
        risk_level = PermitRiskLevel.LOW

    origin_label = _point_label(origin)
    dest_label = _point_label(destination)
    via = f" через {len(waypoints)} промежуточных точек" if waypoints else ""

    if permit_required:
        route_summary = (
            f"Маршрут {origin_label} → {dest_label}{via}: габариты "
            f"{cargo.length_m}×{cargo.width_m}×{cargo.height_m} м, масса {cargo.mass_kg / 1000:.1f} т — "
            "требуется спецразрешение."
        )
    else:
        route_summary = (
            f"Маршрут {origin_label} → {dest_label}{via}: габариты в пределах норм "
            f"({STANDARD_LIMITS_M['length_m']}×{STANDARD_LIMITS_M['width_m']}×{STANDARD_LIMITS_M['height_m']} м)."
        )

    restrictions: list[str] = []
    special_conditions: list[str] = []
    dispatcher_actions: list[str] = []

    if exceeds["width"]:
        restrictions.append(f"Ширина {cargo.width_m} м превышает норму {STANDARD_LIMITS_M['width_m']} м")
    if exceeds["height"]:
        restrictions.append(f"Высота {cargo.height_m} м превышает норму {STANDARD_LIMITS_M['height_m']} м")
    if exceeds["length"]:
        restrictions.append(f"Длина {cargo.length_m} м превышает норму {STANDARD_LIMITS_M['length_m']} м")
    if cargo.mass_kg > 44_000:
        restrictions.append(f"Масса {cargo.mass_kg / 1000:.1f} т — тяжеловес, нужна проверка нагрузки на оси")
    if heavy_axle:
        special_conditions.append(f"Нагрузка на ось до {max_axle / 1000:.1f} т — возможны ограничения на мостах")

    if permit_required:
        dispatcher_actions.extend(
            [
                "Проверить маршрут в ЛК Росдормониторинг (urm.safe-route.ru)",
                "Подготовить схему груза и параметры ТС",
                "Утвердить черновик перед подачей заявки (human-in-the-loop)",
            ]
        )
    if podd_required:
        dispatcher_actions.append("Оценить необходимость ПОДД и согласование с владельцем дороги")

    alternative_routes: list[str] = []
    if permit_required and waypoints:
        alternative_routes.append("Рассмотреть маршрут с меньшим числом ограниченных участков (фаза 3 OSRM)")

    return PermitAnalysisResult(
        permit_required=permit_required,
        podd_required=podd_required,
        risk_level=risk_level,
        risk_score=round(risk_score, 3),
        route_summary=route_summary,
        restrictions=restrictions,
        special_conditions=special_conditions,
        alternative_routes=alternative_routes,
        legal_references=LEGAL_REFERENCES if permit_required else [],
        dispatcher_actions=dispatcher_actions,
        exceeds_limits={
            "width": exceeds["width"],
            "height": exceeds["height"],
            "length": exceeds["length"],
        },
        confidence=0.92 if permit_required else 0.98,
    )
