import re

from django.core.exceptions import ValidationError

NOT_CONVERTIBLE = 'Невозможно конвертировать в цвет!'


def is_convertible_to_color(value):
    if not re.search('^#[0-9A-F]{6}$', value):
        raise ValidationError(NOT_CONVERTIBLE)
    return value
