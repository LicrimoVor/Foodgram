import base64

from core.exception import BadRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import set_value

from profile_user.models import FavoriteModel, FollowModel, ShoppingCartModel
from recipe.models import (IngredientModel, IngredientRecipeModel, RecipeModel,
                           TagModel, TagRecipeModel)

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


class IngredientField(serializers.PrimaryKeyRelatedField):
    """Поле сериализатора для ингредиентов."""

    def to_representation(self, value):
        """Сериализация данных. (в словарь)"""
        instance = self.queryset.filter(ingredient=value).first()
        return {
            "id": value.id,
            "name": value.name,
            "measurement_unit": value.measurement_unit,
            "amount": instance.amount,
        }

    def to_internal_value(self, data):
        """Десериализация данных. (из словаря)"""
        id = data.get('id')
        amount = data.get('amount')

        if not id:
            raise serializers.ValidationError({
                'id': 'Это поле обязательное.'
            })
        if not amount:
            raise serializers.ValidationError({
                'amount': 'Это поле обязательное.'
            })

        if float(amount) < 0:
            raise serializers.ValidationError({
                'amount': 'Значение amount должно быть больше 0.'
            })

        return {
            'id': int(id),
            'amount': float(amount),
        }


class Base64ImageField(serializers.ImageField):
    """Поле для картинок."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    ingredients = IngredientField(
        queryset=IngredientRecipeModel.objects.all(),
        many=True,
        required=True,
    )
    image = Base64ImageField(allow_null=False, required=False,)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    cooking_time = serializers.IntegerField(required=True,)
    tags = TagSerializer(many=True, required=False, allow_null=True)
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
        self.is_valid(True)
        ingredients = validated_data.pop("ingredients")
        tag_recipe_model_list = []
        if 'tags' not in validated_data:
            recipe = RecipeModel(**validated_data)
        else:
            tags_list = validated_data.pop('tags')
            recipe = RecipeModel(**validated_data)
            for tag in tags_list:
                tag_model = get_object_or_404(TagModel, id=tag)
                tag_recipe_model = TagRecipeModel(tag=tag_model, recipe=recipe)
                tag_recipe_model_list.append(tag_recipe_model)

        ingredient_recipe_model_list = []
        for ingredient in ingredients:
            ingr_id = ingredient.pop("id")
            ingredient_model = get_object_or_404(IngredientModel, id=ingr_id)
            ingredient_recipe_model = IngredientRecipeModel(
                recipe=recipe, ingredient=ingredient_model, **ingredient
            )
            ingredient_recipe_model_list.append(ingredient_recipe_model)

        recipe.save()
        IngredientRecipeModel.objects.bulk_create(ingredient_recipe_model_list)
        TagRecipeModel.objects.bulk_create(tag_recipe_model_list)

        return recipe

    def update(self, instance, validated_data):
        queryset_tag = TagRecipeModel.objects.filter(recipe=instance)
        tag_list = []
        for tag_model in enumerate(queryset_tag):
            tag_id = tag_model[1].tag.id
            tag_list.append(tag_id)

        tag_set_original = set(tag_list)
        if validated_data.get('tags') is None:
            tag_set_data: set = {}
        else:
            tag_set_data: set = set(validated_data.get('tags'))

        tag_delete = tag_set_original - tag_set_data
        for tag_id in tag_delete:
            tag_model = get_object_or_404(TagModel, id=tag_id)
            tag_recipe_model = TagRecipeModel(tag=tag_model, recipe=instance)
            tag_recipe_model.delete()

        tag_create = tag_set_data - tag_set_original
        tag_recipe_model_list = []
        for tag_id in tag_create:
            tag_model = get_object_or_404(TagModel, id=tag_id)
            tag_recipe_model = TagRecipeModel(tag=tag_model, recipe=instance)
            tag_recipe_model_list.append(tag_recipe_model)
        TagRecipeModel.objects.bulk_create(tag_recipe_model_list)

        queryset_ingredient = IngredientRecipeModel.objects.filter(
            recipe=instance)
        ingredient_list = []
        for ingredient_model in enumerate(queryset_ingredient):
            ingredient_id = ingredient_model[1].id
            ingredient_list.append(ingredient_id)
        ingredient_set_original = set(ingredient_list)

        ingredients = validated_data.pop("ingredients")
        ingredient_data_list = []
        for ingredient in ingredients:
            ingr_id = ingredient.pop("id")
            ingredient_model = get_object_or_404(IngredientModel, id=ingr_id)
            ingredient_recipe_model = (
                IngredientRecipeModel.objects.get_or_create(
                    recipe=instance, ingredient=ingredient_model, **ingredient
                )[0])
            ingredient_recipe_id = ingredient_recipe_model.id
            ingredient_data_list.append(ingredient_recipe_id)
        ingredient_data_set = set(ingredient_data_list)
        ingredient_delete = ingredient_set_original - ingredient_data_set
        IngredientRecipeModel.objects.filter(id__in=ingredient_delete).delete()
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        if validated_data.get('image'):
            instance.image = validated_data.get('image')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()
        return instance

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

    def validate_tags(self, value):
        """Валидация тегов."""
        if not value:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError("Ожидался список")
        for val in value:
            if not isinstance(val, int):
                raise serializers.ValidationError(
                    "Ожидались значения id (int)")
        return value

    def to_internal_value(self, data):
        """Обход валидации тегов."""
        tag_list = []
        if data.get("tags"):
            tag_list = data.pop("tags")
        ordered_dict = super().to_internal_value(data)
        if tag_list:
            data["tags"] = tag_list
            self.validate_tags(tag_list)
            set_value(ordered_dict, ['tags'], tag_list)
        return ordered_dict


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
        follow_id = self.initial_data.get("follow_id")
        author = get_object_or_404(User, id=follow_id)
        user = self.initial_data.get("user")
        if user.id == follow_id:
            raise BadRequest()

        follow_model = FollowModel.objects.get_or_create(follower=author,
                                                         user=user)
        if follow_model[1] is False:
            raise BadRequest()

        return follow_model[0]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка продуктов."""

    recipe = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ShoppingCartModel
        fields = ('recipe', )

    def create(self, initial_data):
        recipe_id = self.initial_data.get("shopping_cart_id")
        user = self.initial_data.get("user")
        self.recipe = get_object_or_404(RecipeModel, id=recipe_id)
        shoppingCart_model = ShoppingCartModel.objects.get_or_create(
            recipe=self.recipe, user=user)
        if shoppingCart_model[1] is False:
            raise BadRequest()
        return shoppingCart_model[0]

    def get_recipe(self, obj):
        """Получения поля рецептов."""
        serializer = RecipeTwoSerializer(self.recipe)
        return serializer.data

    def to_representation(self, value):
        value_dict = dict(super().to_representation(value))
        result_dict = {**value_dict, }
        return result_dict


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    recipe = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FavoriteModel
        fields = ('recipe', )

    def create(self, initial_data):
        recipe_id = self.initial_data.get("favorite_id")
        user = self.initial_data.get("user")
        recipe = get_object_or_404(RecipeModel, id=recipe_id)
        favorite_model = FavoriteModel.objects.get_or_create(
            recipe=recipe, user=user)
        if favorite_model[1] is False:
            raise BadRequest()
        return favorite_model[0]

    def get_recipe(self, obj):
        """Получения поля рецептов."""
        recipe = obj.recipe
        serializer = RecipeSerializer(recipe, context=self.context)
        return serializer.data

    def to_representation(self, value):
        value_dict = dict(super().to_representation(value))
        result_dict = {**value_dict, }
        return result_dict
