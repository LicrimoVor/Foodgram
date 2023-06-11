
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response

from .viewset import GetViewSet, GetPostDelViewSet, PostDelViewSet
from recipe.models import TagModel, IngredientModel, RecipeModel
from profile_user.models import FollowModel, ShoppingCartModel, FavoriteModel
from .permissions import ModifiPerm, OnlyAuthPerm
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    FavoriteSerializer,
    FollowSerializer,
)


User = get_user_model()


class TagViewSet(GetViewSet):
    """ViewSet модели тегов."""

    queryset = TagModel.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class IngredientSet(GetViewSet):
    """ViewSet модели ингредиентов."""

    queryset = IngredientModel.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class RecipeSet(viewsets.ModelViewSet):
    """ViewSet модели избранных рецептов пользователей."""
    queryset = RecipeModel.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (ModifiPerm, )
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

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context













class GetFollowSet(GetViewSet):
    """ViewSet модели подписок пользователей."""

    queryset = FollowModel.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (OnlyAuthPerm, )

    def get_queryset(self):
        user = self.request.user
        queryset = FollowModel.objects.filter(user=user)
        return queryset


class PostDelFollowView(generics.DestroyAPIView,
                        generics.CreateAPIView,
                        generics.GenericAPIView,):
    """ViewSet модели подписок пользователя."""
    queryset = FollowModel.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (OnlyAuthPerm, )

    def create(self, request, *args, **kwargs):
        data = {
            'user': request.user,
            'follow_id': kwargs.get("follow_id"),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        follow_id = kwargs.get("follow_id")
        author = get_object_or_404(User, id=follow_id)
        user = request.user
        follow_model = get_object_or_404(FollowModel, follower=author, user=user)
        follow_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetShoppingCartSet(GetViewSet):
    """ViewSet модели список купок пользователя."""
    queryset = ShoppingCartModel.objects.all()
    permission_classes = (OnlyAuthPerm, )

    def get_queryset(self):
        user = self.request.user
        return ShoppingCartModel.objects.filter(user=user)

    def get_object(self):
        user = self.request.user
        return ShoppingCartModel.objects.filter(user=user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        content = 'Hello World!'
        return HttpResponse(content, content_type='text/plain')


class PostDelShoppingCartView(generics.DestroyAPIView,
                              generics.CreateAPIView,
                              generics.GenericAPIView,):
    """ViewSet модели список купок пользователя."""
    queryset = ShoppingCartModel.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (OnlyAuthPerm, )

    def get_queryset(self):
        user = self.request.user
        return ShoppingCartModel.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteView(generics.DestroyAPIView,
                   generics.CreateAPIView,
                   generics.GenericAPIView,):
    """ViewSet модели избранных рецептов пользователя."""
    queryset = FavoriteModel.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (OnlyAuthPerm, )

    def create(self, request, *args, **kwargs):
        data = {
            'user': request.user,
            'favorite_id': kwargs.get("favorite_id"),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        recipe_id = kwargs.get("favorite_id")
        recipe = get_object_or_404(RecipeModel, id=recipe_id)
        user = request.user
        favorite_model = get_object_or_404(FavoriteModel, recipe=recipe, user=user)
        favorite_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
