from django.contrib.auth import get_user_model
from django.db import models

from core.validators import (validate_amount_more_zero, validate_hex,
                             validate_min_time)

User = get_user_model()


class TagModel(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name="Название",
        help_text="Название тега",
        max_length=200,
        unique=True,
        null=False,
        blank=False,
    )
    color = models.CharField(
        verbose_name="Цвет",
        help_text="Цвет в HEX-формате",
        max_length=7,
        unique=True,
        null=False,
        blank=False,
        validators=[validate_hex],
    )
    slug = models.SlugField(
        verbose_name="Slug",
        help_text="Slug тега",
        max_length=200,
        unique=True,
        null=False,
        blank=False,
    )

    class Meta:
        ordering = ("id",)
        db_table = "Tag"

    def __str__(self) -> str:
        return self.name


class IngredientModel(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name="Название ингридиента",
        max_length=200,
        null=False,
        blank=False,
    )
    measurement_unit = models.CharField(
        verbose_name="Ед. измерения",
        max_length=200,
        null=False,
        blank=False,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("id",)
        db_table = "Ingredient"
        unique_together = ('name', 'measurement_unit',)


class RecipeModel(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        null=False,
        blank=False,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name="Название",
        help_text="Название рецепта",
        max_length=200,
        null=False,
        blank=False,
    )
    text = models.TextField(
        verbose_name="Описание",
        help_text="Описание рецепта",
        null=False,
        blank=False,
    )
    image = models.ImageField(
        verbose_name="Фото блюда",
        upload_to="recipe/image/",
        null=False,
        blank=False,
    )
    cooking_time = models.IntegerField(
        verbose_name="Время (мин.)",
        help_text="Время приготовления в минутах",
        null=False,
        blank=False,
        validators=[validate_min_time]
    )
    tags = models.ManyToManyField(
        TagModel,
        verbose_name="Теги",
        through="TagRecipeModel",
    )
    ingredients = models.ManyToManyField(
        IngredientModel,
        verbose_name="Ингрендиенты",
        through="IngredientRecipeModel"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("-id",)
        db_table = "Recipe"


class TagRecipeModel(models.Model):
    """Модель связи тегов и рецептов."""

    tag = models.ForeignKey(
        TagModel,
        verbose_name="Тег (id)",
        on_delete=models.CASCADE,
        related_name='tag_recipe',
    )
    recipe = models.ForeignKey(
        RecipeModel,
        verbose_name="Рецепт (id)",
        on_delete=models.CASCADE,
        related_name='tag_recipe',
    )

    def __str__(self) -> str:
        return f'{self.recipe} {self.tag}'

    class Meta:
        ordering = ("id",)
        db_table = "Recipe-Tag"


class IngredientRecipeModel(models.Model):
    """Модель связи тегов и рецептов."""

    ingredient = models.ForeignKey(
        IngredientModel,
        verbose_name="Ингредиент (id)",
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name='ingredient_recipe',
    )
    recipe = models.ForeignKey(
        RecipeModel,
        verbose_name="Рецепт (id)",
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
    )
    amount = models.FloatField(
        verbose_name="Кол-во ингредиента",
        null=False,
        blank=False,
        validators=[validate_amount_more_zero]
    )

    def __str__(self) -> str:
        return f'{self.recipe} {self.ingredient} {self.amount}'

    class Meta:
        ordering = ("id",)
        db_table = "Recipe-Ingredient"
        unique_together = ["ingredient", "recipe"]
