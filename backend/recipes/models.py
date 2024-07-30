import string
import random
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from foodgram import constants

from .validators import validate_amount, validate_cooking_time


class Tag(models.Model):
    name = models.CharField(
        max_length=constants.MAX_TAG_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        max_length=constants.MAX_TAG_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=constants.MAX_INGREDIENT_NAME_LENGTH
    )
    measurement_unit = models.CharField(
        max_length=constants.MAX_MEASUREMENT_UNIT_LENGHT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=constants.MAX_RECIPE_NAME_LINGHT,
        verbose_name='Название',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=True,
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[validate_cooking_time,
                    MinValueValidator(constants.MIN_VALUE_COOCKING_TIME),
                    MaxValueValidator(constants.MAX_VALUE_COOCKING_TIME)]
    )
    short_url = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Короткая ссылка'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']

    def __str__(self):
        return self.name

    def generate_short_url(self):
        characters = string.ascii_letters + string.digits
        while True:
            short_url = ''.join(
                random.choice(characters) for _ in range(constants.LENGTH_URL))
            if not Recipe.objects.filter(short_url=short_url).exists():
                return short_url

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = self.generate_short_url()
        super().save(*args, **kwargs)


class RecipeUserModel(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='%(class)ss',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='%(class)ss',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_together_recipe_user'
            )
        ]
        ordering = ['recipe', 'user']


class Favorite(RecipeUserModel):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe.name} в избраннном у {self.user.username}'


class ShoppingCart(RecipeUserModel):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (f'{self.recipe.name} в списке покупок у '
                f'{self.user.username}')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[validate_amount,
                    MinValueValidator(constants.MIN_VALUE_AMOUNT),
                    MaxValueValidator(constants.MAX_VALUE_AMOUNT)]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
