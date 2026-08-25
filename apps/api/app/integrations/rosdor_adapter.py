"""Росдормониторинг adapter — фаза 1 (stub + parser API hook)."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.schemas.permit import RosdorHealthResponse, RosdorPermitCheckResponse


@dataclass
class RosdorAdapter:
    settings: Settings

    @property
    def parser_configured(self) -> bool:
        return bool(self.settings.rosdor_parser_api_key and self.settings.rosdor_parser_base_url)

    def health(self) -> RosdorHealthResponse:
        if self.parser_configured:
            return RosdorHealthResponse(
                configured=True,
                parser_api_enabled=True,
                lk_enabled=self.settings.rosdor_lk_enabled,
                status="ready",
                message="Parser API credentials configured (live calls — Sprint 7.1)",
            )
        return RosdorHealthResponse(
            configured=False,
            parser_api_enabled=False,
            lk_enabled=False,
            status="stub",
            message="ROSDOR_PARSER_API_KEY not set — using demo responses",
        )

    async def check_permit(self, permit_number: str, plate: str) -> RosdorPermitCheckResponse:
        """Проверка разрешения в реестре. Live API — когда задан ROSDOR_PARSER_API_KEY."""
        if self.parser_configured:
            # TODO Sprint 7.1: httpx call to parser-api.com
            return RosdorPermitCheckResponse(
                found=False,
                permit_number=permit_number,
                plate=plate.upper(),
                status=None,
                source="parser_api_pending",
            )

        # Demo stub для разработки UI
        demo_number = permit_number.upper().startswith("DEMO")
        return RosdorPermitCheckResponse(
            found=demo_number,
            permit_number=permit_number,
            plate=plate.upper(),
            status="active" if demo_number else None,
            valid_until="2026-12-31" if demo_number else None,
            route_summary="М-11, участок 120–145 км" if demo_number else None,
            special_conditions=["Движение только в светлое время суток"] if demo_number else [],
            source="stub",
        )


def get_rosdor_adapter() -> RosdorAdapter:
    return RosdorAdapter(settings=get_settings())
