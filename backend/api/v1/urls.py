from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteView, GetFollowSet, GetShoppingCartSet,
                    IngredientSet, PostDelFollowView, PostDelShoppingCartView,
                    RecipeSet, TagSet)

router = DefaultRouter()
router.register("tags", TagSet, basename="tags")
router.register("ingredients", IngredientSet, basename="ingredients")
router.register("recipes/download_shopping_cart",
                GetShoppingCartSet, basename="get_shopping_cart")
router.register("recipes", RecipeSet, basename="recipes")
router.register("users/subscriptions", GetFollowSet, basename="get_follow")


urlpatterns = [
    path("", include(router.urls)),
    path("recipes/<int:favorite_id>/favorite/",
         FavoriteView.as_view(), name='post_del_favorite'),
    path("users/<int:follow_id>/subscribe/",
         PostDelFollowView.as_view(), name='post_del_follow'),
    path("recipes/<int:shopping_cart_id>/shopping_cart/",
         PostDelShoppingCartView.as_view(), name='post_del_shopping_cart'),
]
