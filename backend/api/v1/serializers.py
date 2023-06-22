import base64

from core.exception import BadRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from profile_user.models import FavoriteModel, FollowModel, ShoppingCartModel
from recipe.models import (IngredientModel, IngredientRecipeModel, RecipeModel,
                           TagModel)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """Получение поля подписки."""
        user = self.context.get('request').user
        if isinstance(user, AnonymousUser):
            return False
        model = FollowModel.objects.filter(follower=obj, user=user)
        if model:
            return True
        return False

    def to_internal_value(self, data):
        user = self.context.get('request').user
        data_dict = super().to_representation(user)
        data_dict.pop('is_subscribed')
        return data_dict


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = TagModel
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = IngredientModel
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Поле сериализатора для ингредиентов."""
    id = serializers.IntegerField(source='ingredient.id', required=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientRecipeModel
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_id(self, value):
        get_object_or_404(IngredientModel, id=value)
        return value


class Base64ImageField(serializers.ImageField):
    """Поле для картинок."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Вспомогательное поле для тегов."""

    def to_representation(self, value):
        serializer = TagSerializer(value)
        return serializer.data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    ingredients = IngredientRecipeSerializer(many=True, required=True,
                                             source='ingredient_recipe')
    image = Base64ImageField(allow_null=False, required=False,)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    cooking_time = serializers.IntegerField(required=True,)
    tags = TagPrimaryKeyRelatedField(queryset=TagModel.objects.all(),
                                     many=True)
    author = UserSerializer(required=False)

    class Meta:
        model = RecipeModel
        fields = ('id',
                  'author',
                  'name',
                  'text',
                  'image',
                  'cooking_time',
                  'tags',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  )

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredient_recipe")
        tags = validated_data.pop('tags')
        recipe = RecipeModel.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.save_ingredinets(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredient_recipe")
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.save_ingredinets(ingredients, instance)
        return super().update(instance, validated_data)

    def get_is_favorited(self, obj):
        """Получение поля избранного."""
        user = self.context.get('request').user
        if isinstance(user, AnonymousUser):
            return False
        model = FavoriteModel.objects.filter(recipe=obj, user=user)
        if model:
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        """Получение поля покупки."""
        user = self.context.get('request').user
        if isinstance(user, AnonymousUser):
            return False
        model = ShoppingCartModel.objects.filter(recipe=obj, user=user)
        if model:
            return True
        return False

    def validate_ingredients(self, value):
        """Валидация ингредиентов."""
        indx_list = []
        for ingredient in value:
            ingr_indx = ingredient['ingredient']['id']
            if ingr_indx in indx_list:
                raise serializers.ValidationError(
                    "Не должно быть одинаковых ингредиентов.")
            indx_list.append(ingr_indx)
        return value

    def save_ingredinets(self, ingredients, recipe):
        """Создаем и сохраняет ингредиента для рецепта."""

        ingredient_recipe_model_list = []
        for ingredient in ingredients:
            ingr_id = ingredient['ingredient'].pop("id")
            amount = ingredient['amount']
            ingredient_model = IngredientModel.objects.get(id=ingr_id)
            ingredient_recipe_model = IngredientRecipeModel(
                recipe=recipe, ingredient=ingredient_model, amount=amount
            )
            ingredient_recipe_model_list.append(ingredient_recipe_model)

        recipe.ingredient_recipe.set(
            ingredient_recipe_model_list, bulk=False
        )


class RecipeTwoSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор. Отвечает только за визуализацию."""

    class Meta:
        model = RecipeModel
        fields = ('id', 'name', 'image', 'cooking_time',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    follower = UserSerializer(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FollowModel
        fields = ('follower', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        """Получения поля кол-ва рецептов."""
        count_queryset = self.recipe_queryset.count()
        return count_queryset

    def get_recipes(self, obj):
        """Получения поля рецептов."""
        author = obj.follower
        self.recipe_queryset = RecipeModel.objects.filter(author=author)
        serializer = RecipeTwoSerializer(self.recipe_queryset, many=True)
        return serializer.data

    def to_representation(self, value):
        value_dict = dict(super().to_representation(value))
        follower_dict = value_dict.pop("follower")
        result_dict = {**value_dict, **follower_dict}
        return result_dict

    def create(self, validated_data):
        author = self.initial_data.get('author')
        user = self.initial_data.get("user")
        follow_model = FollowModel.objects.create(follower=author,
                                                  user=user)
        return follow_model

    def validate_empty_values(self, data):
        """Валидация данных."""
        follow_id = data.pop("follow_id")
        author = get_object_or_404(User, id=follow_id)
        user = data.get("user")
        if user.id == follow_id:
            raise BadRequest()
        if FollowModel.objects.filter(follower=author, user=user).first():
            raise BadRequest()
        data['author'] = author
        return super().validate_empty_values(data)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка продуктов."""

    recipe = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ShoppingCartModel
        fields = ('recipe', )

    def create(self, initial_data):
        recipe = self.initial_data.get("shoppingcart")
        user = self.initial_data.get("user")
        shoppingCart_model = ShoppingCartModel.objects.create(
            recipe=recipe, user=user)
        return shoppingCart_model

    def get_recipe(self, obj):
        """Получения поля рецептов."""
        serializer = RecipeTwoSerializer(self.recipe)
        return serializer.data

    def to_representation(self, value):
        value_dict = dict(super().to_representation(value))
        result_dict = {**value_dict, }
        return result_dict

    def validate_empty_values(self, data):
        """
        В ReDoc описано 'при ошбике выдавать 400'
        (например, при попытке добавить уже существующую или удалить
        уже не существующую модель), тело ответа:
        {"errors": "string"}. Или это все лишнее?
        """
        recipe_id = data.pop("favorite_id")
        recipe_model = get_object_or_404(RecipeModel, id=recipe_id)
        user = data.get("user")
        if ShoppingCartModel.objects.filter(user=user,
                                            recipe=recipe_model).first():
            raise BadRequest()
        data["shoppingcart"] = recipe_model
        return super().validate_empty_values(data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    recipe = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FavoriteModel
        fields = ('recipe', )

    def create(self, initial_data):
        recipe = self.initial_data.get("favorite")
        user = self.initial_data.get("user")
        favorite_model = FavoriteModel.objects.create(
            recipe=recipe, user=user)
        return favorite_model

    def get_recipe(self, obj):
        """Получения поля рецептов."""
        recipe = obj.recipe
        serializer = RecipeSerializer(recipe, context=self.context)
        return serializer.data

    def to_representation(self, value):
        value_dict = dict(super().to_representation(value))
        result_dict = {**value_dict, }
        return result_dict

    def validate_empty_values(self, data):
        """
        В ReDoc описано 'при ошбике выдавать 400'
        (например, при попытке добавить уже существующую или удалить
        уже не существующую модель), тело ответа:
        {"errors": "string"}. Или это все лишнее?
        """
        recipe_id = data.pop("favorite_id")
        recipe_model = get_object_or_404(RecipeModel, id=recipe_id)
        user = data.get("user")
        if FavoriteModel.objects.filter(user=user,
                                        recipe=recipe_model).first():
            raise BadRequest()
        data["favorite"] = recipe_model
        return super().validate_empty_values(data)
