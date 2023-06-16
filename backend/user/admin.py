from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from profile_user.admin import (FavoriteInline, FollowInline,
                                ShoppingCartInline, SubscriptionInline)

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    """Отображение пользователей в панеле администратора."""

    list_filter = ('email', 'username')
    inlines = [
        FavoriteInline,
        ShoppingCartInline,
        FollowInline,
        SubscriptionInline,
    ]


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
