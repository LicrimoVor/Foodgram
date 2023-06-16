from django.contrib import admin
from profile_user.models import FavoriteModel
from recipe.models import (IngredientModel, IngredientRecipeModel, RecipeModel,
                           TagModel, TagRecipeModel)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipeModel
    extra = 1


class TagInline(admin.TabularInline):
    model = TagRecipeModel
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Отображение рецептов в панеле администратора."""
    list_display = ("name", "author")
    list_filter = ("author", "name", "tags")
    readonly_fields = ("favorite_count", )

    def favorite_count(self, obj):
        return len(FavoriteModel.objects.filter(recipe=obj))

    favorite_count.short_description = "Количество фаворитов"
    inlines = [
        IngredientInline,
        TagInline,
    ]


class TagAdmin(admin.ModelAdmin):
    """Отображение тегов в панеле администратора."""
    list_display = ("name", "slug", "color")
    list_filter = ("name", "slug")


class IngredientAdmin(admin.ModelAdmin):
    """Отображение ингредиентов в панеле администратора."""
    list_display = ("name", "measurement_unit")
    list_filter = ("name", )


admin.site.register(RecipeModel, RecipeAdmin)
admin.site.register(TagModel, TagAdmin)
admin.site.register(IngredientModel, IngredientAdmin)
