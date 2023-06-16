from django.contrib.auth import get_user_model
from django.db import models
from recipe.models import RecipeModel

User = get_user_model()


class FollowModel(models.Model):
    """Модель подписок пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='followers',
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        related_name='subscribers',
    )

    class Meta:
        ordering = ("id",)
        db_table = "Follow"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'follower'], name='unique_together',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("follower")),
                name='user_neq'
            )
        ]


class FavoriteModel(models.Model):
    """Модель избранных рецептов."""

    recipe = models.ForeignKey(
        RecipeModel,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorites",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites",
    )

    class Meta:
        ordering = ("id",)
        db_table = "Favorite"
        unique_together = ('recipe', 'user')


class ShoppingCartModel(models.Model):
    """Модель рецептов в корзине пользователя."""

    recipe = models.ForeignKey(
        RecipeModel,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="shopping",
    )

    class Meta:
        ordering = ("id",)
        db_table = "ShoppingCart"
        unique_together = ('recipe', 'user')
