from rest_framework import serializers


from .user_serializer import UserSerializer
from ..validators import validate_username
from foodgram.serializers import RecipeMinifiedSerializer


class UserDataSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[validate_username]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)


class CustomUserCreateSerializer(UserDataSerializer):
    password = serializers.CharField(max_length=150)


class CustomUserResponseOnCreateSerializer(UserDataSerializer):
    id = serializers.IntegerField()


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['recipes']

    def get_recipes(self, obj):
        limit = int(
            self.context['request'].query_params.get('recipes_limit', 10)
        )
        limit = max(1, min(100, limit))
        recipes = obj.recipes.all()[:limit]
        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()
