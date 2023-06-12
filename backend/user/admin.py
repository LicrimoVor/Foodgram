from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from profile_user.models import FavoriteModel, FollowModel, ShoppingCartModel


class FavoriteInline(admin.TabularInline):
    model = FavoriteModel
    extra = 1
    verbose_name_plural = "Избранные рецепты"


class SubscriptionInline(admin.TabularInline):
    model = FollowModel
    fk_name = "user"
    extra = 1
    verbose_name_plural = "Подписки"


class FollowInline(admin.TabularInline):
    model = FollowModel
    verbose_name_plural = "Фолловеры"
    extra = 1
    fk_name = "follower"


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCartModel
    verbose_name_plural = "Корзина рецептов"
    extra = 1


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
