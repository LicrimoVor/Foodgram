from django.core.exceptions import ValidationError
import re


def validate_hex(hex_string: str) -> None:
    """Проверка hex-строки на образец hex."""
    if re.fullmatch(r"#[A-F0-9]{6,6}", hex_string) is None:
        raise ValidationError(
            message=f"Цвет должен быть в формате HEX! Строка {hex_string}\
                     не является строкой HEX-формата",
            params={"color": hex_string},
        )

def validate_min_time(time: float) -> None:
    """Проверка времени на условие time > 1."""
    if time < 1:
        raise ValidationError(
            message="Время приготовления не может быть меньше 1.",
            params={"cooking_time": time},
        )

def validate_amount_more_zero(amount: float) -> None:
    """Проверка на значение > 0."""
    if amount <= 0:
        raise ValidationError(
            message="Количество ингридиента не может быть\
                     меньше или равен 0",
            params={"amount": amount},
        )

def validate_correct_username(username: str) -> None:
    """Проверка никнейма пользователя на корректность."""
    if re.fullmatch(r"^[\w.@+-]+\Z", username) is None:
        raise ValidationError(
            message="Никнейм пользователя введен неверно.\
                     Никнейм может содержать латинские буквы верхнего и нижнего регистра\
                     цифры, а так же символы . @ + -",
            params={"username": username},
        )
