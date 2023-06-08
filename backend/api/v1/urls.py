from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TagViewSet,
    IngredientSet,
    RecipeSet
)

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientSet, basename="ingredients")
router.register("recipe", RecipeSet, basename="recipe")

urlpatterns = [
    path("", include(router.urls)),
]
