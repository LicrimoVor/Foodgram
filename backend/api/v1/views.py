from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .viewset import GetViewSet, GetPostDelViewSet
from recipe.models import TagModel, IngredientModel, RecipeModel
from profile_user.models import FollowModel, ShoppingCartModel
from .permissions import ModifiPerm, OnlyAuthPerm

User = get_user_model()


class TagViewSet(GetViewSet):
    """ViewSet модели тегов."""

    queryset = TagModel.objects.all()
    serializer_class = ...
    permission_classes = (OnlyAuthPerm, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class IngredientSet(GetViewSet):
    """ViewSet модели ингредиентов."""

    queryset = IngredientModel.objects.all()
    serializer_class = ...
    permission_classes = (OnlyAuthPerm, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class SubscriptionSet(GetPostDelViewSet):
    """ViewSet модели подписок пользователей."""

    queryset = FollowModel.objects.all()
    serializer_class = ...
    permission_classes = (OnlyAuthPerm, )

    def get_queryset(self):
        user = self.request.user
        return FollowModel.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteSet(GetPostDelViewSet):
    """ViewSet модели избранных рецептов пользователей."""
    queryset = FollowModel.objects.all()
    serializer_class = ...
    permission_classes = (OnlyAuthPerm, )

    def get_queryset(self):
        user = self.request.user
        return FollowModel.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShoppingCartSet(GetPostDelViewSet):
    """ViewSet модели избранных рецептов пользователей."""
    queryset = ShoppingCartModel.objects.all()
    serializer_class = ...
    permission_classes = (OnlyAuthPerm, )

    def get_queryset(self):
        user = self.request.user
        return ShoppingCartModel.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class RecipeSet(GetPostDelViewSet):
    """ViewSet модели избранных рецептов пользователей."""
    queryset = RecipeModel.objects.all()
    serializer_class = ...
    permission_classes = (OnlyAuthPerm, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ("text",)
    filterset_fields = (
        "tags",
        "name",
        "author",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.get("tags", None)

        if tags is not None:
            queryset = queryset.filter(tags=tags)

        return queryset()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
