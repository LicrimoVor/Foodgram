from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

from profile_user.models import FavoriteModel, FollowModel, ShoppingCartModel
from recipe.models import (IngredientModel, IngredientRecipeModel, RecipeModel,
                           TagModel)
from .filterset import (FavoriteRecipeFilter, IngredientFilter,
                        TagsRecipeFilter, ShoppingRecipeFilter)
from .pagination import CustomPagination
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .viewset import GetViewSet

User = get_user_model()


class TagSet(GetViewSet):
    """ViewSet модели тегов."""

    queryset = TagModel.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "slug")
    pagination_class = CustomPagination


class IngredientSet(GetViewSet):
    """ViewSet модели ингредиентов."""

    queryset = IngredientModel.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = (IngredientFilter,)
    pagination_class = CustomPagination


class RecipeSet(viewsets.ModelViewSet):
    """ViewSet модели рецептов пользователей."""
    queryset = RecipeModel.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (filters.SearchFilter,
                       TagsRecipeFilter,
                       FavoriteRecipeFilter,
                       ShoppingRecipeFilter)
    search_fields = ("text",)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.to_internal_value(request.data)
        return super().update(request, *args, **kwargs)


class GetFollowSet(GetViewSet):
    """ViewSet модели подписок пользователей, только Get-запросы."""

    queryset = FollowModel.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        queryset = FollowModel.objects.filter(user=user)
        return queryset


class PostDelFollowView(generics.DestroyAPIView,
                        generics.CreateAPIView,
                        generics.GenericAPIView,):
    """ViewSet модели подписок пользователя, только Post и Del-запросы."""
    queryset = FollowModel.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        data = {
            'user': request.user,
            'follow_id': kwargs.get("follow_id"),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        follow_id = kwargs.get("follow_id")
        author = get_object_or_404(User, id=follow_id)
        user = request.user
        follow_model = get_object_or_404(FollowModel,
                                         follower=author, user=user)
        follow_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetShoppingCartSet(GetViewSet):
    """ViewSet модели покупок пользователя, только Get-запросы."""
    queryset = ShoppingCartModel.objects.all()
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return ShoppingCartModel.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset_shop = self.get_queryset()
        ingredient_data = self.get_ingredient_data(queryset_shop)
        content = ""
        for key, value in ingredient_data.items():
            string_row = f"{key} — {value} \n"
            content += string_row
        response = HttpResponse(content, content_type="text/plain")
        response['Content-Disposition'] = 'attachment; filename=file.txt'
        return response

    def get_ingredient_data(self, queryset_shop) -> dict:
        ingredient_data = {}

        for shop_model in enumerate(queryset_shop):
            recipe_model = shop_model[1].recipe
            queryset_ingredient = IngredientRecipeModel.objects.filter(
                recipe=recipe_model)

            for ingredient_model in enumerate(queryset_ingredient):
                name = ingredient_model[1].ingredient.name
                measurement_unit = (
                    ingredient_model[1].ingredient.measurement_unit)
                amount = ingredient_model[1].amount
                key = f"{name} ({measurement_unit})"
                if ingredient_data.get(key) is None:
                    ingredient_data[key] = amount
                else:
                    ingredient_data[key] += amount

        return ingredient_data


class PostDelShoppingCartView(generics.DestroyAPIView,
                              generics.CreateAPIView,
                              generics.GenericAPIView,):
    """ViewSet модели покупок пользователя, только Post и Del-запросов."""
    queryset = ShoppingCartModel.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        data = {
            'user': request.user,
            'shopping_cart_id': kwargs.get("shopping_cart_id"),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        recipe_id = kwargs.get("shopping_cart_id")
        recipe = get_object_or_404(RecipeModel, id=recipe_id)
        user = request.user
        favorite_model = get_object_or_404(ShoppingCartModel,
                                           recipe=recipe, user=user)
        favorite_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(generics.DestroyAPIView,
                   generics.CreateAPIView,
                   generics.GenericAPIView,):
    """
    ViewSet модели избранных рецептов пользователя,
    только Post и Del-запросы.
    """
    queryset = FavoriteModel.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        data = {
            'user': request.user,
            'favorite_id': kwargs.get("favorite_id"),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        recipe_id = kwargs.get("favorite_id")
        recipe = get_object_or_404(RecipeModel, id=recipe_id)
        user = request.user
        favorite_model = get_object_or_404(FavoriteModel,
                                           recipe=recipe, user=user)
        favorite_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
