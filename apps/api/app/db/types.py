from enum import Enum

from sqlalchemy import Enum as SAEnum


def pg_str_enum(enum_cls: type[Enum], name: str, **kwargs) -> SAEnum:
    """PostgreSQL enum column for str-backed Python enums (stores .value, not .name)."""
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=True,
        values_callable=lambda members: [member.value for member in members],
        **kwargs,
    )
