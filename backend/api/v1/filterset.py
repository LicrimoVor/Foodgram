from django.db.models import Q
from recipe.models import RecipeModel
from rest_framework.filters import BaseFilterBackend


class IngredientFilter(BaseFilterBackend):
    """Фильтрация ингредиента по имени."""

    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('name'):
            string_name = request.query_params['name']
            queryset = (
                queryset.filter(Q(name__iendswith=string_name)
                                | Q(name__istartswith=string_name))
            )
        return queryset


class TagsRecipeFilter(BaseFilterBackend):
    """Фильтрация рецептов по тегу."""

    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('tags'):
            tags_list = request.query_params.getlist('tags')
            queryset = queryset.filter(tags__slug__in=tags_list).distinct()
        return queryset


class FavoriteRecipeFilter(BaseFilterBackend):
    """Фильтрация рецептов по избранному."""

    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('is_favorited'):
            user = request.user
            queryset_2 = (
                RecipeModel.objects.prefetch_related(
                    'favorites').filter(favorites__user=user)).distinct()
            queryset = queryset_2 & queryset.distinct()
        return queryset


class ShoppingRecipeFilter(BaseFilterBackend):
    """Фильтрация рецептов по корзине покупок."""

    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('is_in_shopping_cart'):
            user = request.user
            queryset_2 = (
                RecipeModel.objects.prefetch_related(
                    'shopping').filter(shopping__user=user)).distinct()
            queryset = queryset_2 & queryset.distinct()
        return queryset
