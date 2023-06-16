import re

from django.core.exceptions import ValidationError


def validate_hex(hex_string: str) -> None:
    """Проверка hex-строки на образец hex."""
    if re.fullmatch(r"#[A-F0-9]{6,6}", hex_string) is None:
        raise ValidationError(
            message=f"Цвет должен быть в формате HEX! Строка {hex_string}\
                     не является строкой HEX-формата",
            params={"color": hex_string},
        )
