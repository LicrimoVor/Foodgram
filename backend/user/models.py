from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserModel(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[AbstractUser.username_validator, ],
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
    )
    email = models.EmailField(
        _('email address'),
        max_length=254,
        unique=True,
    )
    groups = None
    # костыль
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name']

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("id",)
