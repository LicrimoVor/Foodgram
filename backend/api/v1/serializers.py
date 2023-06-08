# import base64
# import datetime as dt
import base64
# import webcolors
# from django.core.files.base import ContentFile
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from recipe.models import (
    TagModel,
    RecipeModel,
    IngredientModel,
    IngredientRecipeModel,
    TagRecipeModel,
)
from profile_user.models import (
    FavoriteModel,
    FollowModel,
    ShoppingCartModel,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "is_subscribed",)

    def get_is_subscribed(self, obj):
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
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

    def get_queryset(self):
        ...


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    tags = TagSerializer(many=True, required=False,)
    ingredients = IngredientField(
        queryset=IngredientRecipeModel.objects.all(),
        many=True)
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = UserSerializer()

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
        ingredients = validated_data.pop("ingredients")
        if 'tags' not in self.initial_data:
            recipe = RecipeModel.objects.create(**validated_data)
        else:
            tags_list = validated_data.pop('tags')
            recipe = RecipeModel.objects.create(**validated_data)
            tag_recipe_model_list = []
            for tag in tags_list:
                tag_model = get_object_or_404(TagModel, id=tag)
                tag_recipe_model = TagRecipeModel(tag=tag_model, recipe=recipe)
                tag_recipe_model_list.append(tag_recipe_model)
            TagRecipeModel.objects.bulk_create(tag_recipe_model_list)
        
        ingredient_recipe_model_list = []
        for ingredient in ingredients:
            ingr_id = ingredient.pop("id")
            ingredient_model = get_object_or_404(IngredientModel, id=ingr_id)
            ingredient_recipe_model = IngredientRecipeModel.objects.create(
                recipe=recipe, ingredient=ingredient_model, **ingredient
            )
            ingredient_recipe_model_list.append(ingredient_recipe_model)
        IngredientRecipeModel.objects.bulk_create(ingredient_recipe_model_list)
        
        return recipe

    def update(self, instance, validated_data):
        """Возможно местами 'дубовато'. Обновление модели."""

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
            tag_model.delete()

        tag_create = tag_set_data - tag_set_original
        tag_recipe_model_list = []
        for tag_id in tag_create:
            tag_recipe_model = TagRecipeModel(tag=tag_id, recipe=instance)
            tag_recipe_model_list.append(tag_recipe_model)
        TagRecipeModel.objects.bulk_create(tag_recipe_model_list)

        queryset_ingredient = IngredientRecipeModel.objects.filter(recipe=instance)
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
            ingredient_recipe_model = IngredientRecipeModel.objects.get_or_create(
                recipe=instance, ingredient=ingredient_model, **ingredient
            )[0]
            ingredient_recipe_id = ingredient_recipe_model.id
            ingredient_data_list.append(ingredient_recipe_id)
        ingredient_data_set = set(ingredient_data_list)
        ingredient_delete = ingredient_set_original - ingredient_data_set
        IngredientRecipeModel.objects.filter(id__in=ingredient_delete).delete()
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.image = validated_data.get('image')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if isinstance(user, AnonymousUser):
            return False
        model = FavoriteModel.objects.filter(recipe=obj, user=user)
        if model:
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
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
        if not isinstance(value[0], int):
            raise serializers.ValidationError("Ожидались значения id (int)")
        return value

    def to_internal_value(self, data):
        """Так как ожидается словарь в ключе tags, то обойдем валидацию))."""
        user = self.context.get('request').user
        if data.get("tags"):
            tag_list = data.pop("tags")
            data["author"] = user.id
            super().to_internal_value(data)
            data["tags"] = tag_list
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = FavoriteModel
        fields = ('id', 'name', 'color', 'slug')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = FollowModel
        fields = ('id', 'name', 'color', 'slug')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка продуктов."""

    class Meta:
        model = ShoppingCartModel
        fields = ('id', 'name', 'color', 'slug')


