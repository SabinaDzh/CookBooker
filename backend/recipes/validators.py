from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    if value < 1 or value > 200:
        raise ValidationError(
            'Допустимое количество времени от 1 до 200 минут'
        )


def validate_amount(value):
    if value < 1 or value > 1000:
        raise ValidationError(
            'Допустимое количество ингредиентов от 1 до 1000'
        )
