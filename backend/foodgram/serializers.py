from rest_framework import serializers

from core.fields import ObjectExistsInUserRelatedManagerField
from core.utils import OverrideRootPartialMixin
from users.serializers import UserSerializer
from .fields import Base64ImageField
from .models import Ingredient, Recipe, RecipeIngredient, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time',
        ]


class RecipeIngredientSerializer(OverrideRootPartialMixin, serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f'Ингредиент с id {value} не найден'
            )
        return value


class RecipeCreateUpdateSerializer(BaseRecipeSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Список ингредиентов не может быть пустым')
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Список тегов не может быть пустым')
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe(**validated_data)
        recipe.save()
        for ingredient in ingredients:
            recipe.ingredients.add(
                ingredient['id'],
                through_defaults={'amount': ingredient['amount']}
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if ingredients:
            instance.ingredients.clear()
        for ingredient in ingredients:
            instance.ingredients.add(
                ingredient['id'],
                through_defaults={'amount': ingredient['amount']}
            )
        if tags:
            instance.tags.set(tags, clear=True)
        instance.save()
        return instance


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = [
            'id', 'name',
            'measurement_unit', 'amount',
        ]


class RecipeListSerializer(BaseRecipeSerializer):
    ingredients = IngredientInRecipeSerializer(many=True, source='recipe_ingredients')
    tags = TagSerializer(many=True)
    author = UserSerializer()
    is_favorited = ObjectExistsInUserRelatedManagerField('favorite_recipes')
    is_in_shopping_cart = ObjectExistsInUserRelatedManagerField('shopping_cart_recipes')

    class Meta(BaseRecipeSerializer.Meta):
        fields = BaseRecipeSerializer.Meta.fields + [
            'id', 'author',
            'is_favorited', 'is_in_shopping_cart',
        ]


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id', 'name',
            'image', 'cooking_time',
        ]
