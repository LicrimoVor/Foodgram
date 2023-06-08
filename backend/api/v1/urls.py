from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TagViewSet,
    IngredientSet,
    RecipeSet,
    FavoriteSet,
    FollowModel,
    ShoppingCartModel,
)

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientSet, basename="ingredients")
router.register(r"recipes/(?P<recipe_id>\d+)/favorite", FavoriteSet, basename="favorite")
router.register(r"recipes/(?P<recipe_id>\d+)/shopping_cart", ShoppingCartModel, basename="favorite")
router.register("recipes", RecipeSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
]
