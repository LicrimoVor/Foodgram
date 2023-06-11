from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.validators import validate_correct_username


class UserModel(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=False,
        blank=False,
        validators=[validate_correct_username, ],
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        null=False,
        blank=False,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        null=False,
        blank=False,
    )
    email = models.EmailField(
        _('email address'),
        max_length=254,
        null=False,
        blank=False,
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
