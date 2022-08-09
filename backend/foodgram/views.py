import os

from django.http import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, Tag
from .pagination import RecipePagination
from .permissions import IsReadOnlyOrIsAuthor
from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeMinifiedSerializer,
    RecipeListSerializer,
    TagSerializer,
)
from core.utils import user_related_create_destroy_action


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    model = Tag
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    model = Ingredient
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    model = Recipe
    serializer_class = RecipeListSerializer
    queryset = Recipe.objects.all()
    permission_classes = [IsReadOnlyOrIsAuthor]
    pagination_class = RecipePagination
    filterset_class = RecipeFilter

    def create(self, request):
        serializer = RecipeCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(author=request.user)
        dirname, filename = os.path.split(instance.image.path)
        filename, extension = os.path.splitext(filename)
        new_filename = f'{instance.id}{extension}'
        new_path = os.path.join(dirname, new_filename)
        os.rename(instance.image.path, new_path)
        dirname, filename = os.path.split(instance.image.name)
        instance.image.name = os.path.join(dirname, new_filename)
        instance.save()
        return Response(
            RecipeListSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        return self.http_method_not_allowed(request)

    def partial_update(self, request, pk=None):
        instance = self.get_object()
        serializer = RecipeCreateUpdateSerializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(RecipeListSerializer(instance).data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return user_related_create_destroy_action(
            self, request, pk,
            manager_name='shopping_cart_recipes',
            already_exists_error='Рецепт уже добавлен в список покупок',
            not_exists_error='Рецепт отсутствует в списке покупок',
            serializer_class=RecipeMinifiedSerializer
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='favorite',
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        return user_related_create_destroy_action(
            self, request, pk,
            manager_name='favorite_recipes',
            already_exists_error='Рецепт уже добавлен в избранное',
            not_exists_error='Рецепт отсутствует в избранном',
            serializer_class=RecipeMinifiedSerializer
        )

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = {}
        for recipe in request.user.shopping_cart_recipes.all():
            for recipe_ingredient in recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient
                amount = recipe_ingredient.amount
                if ingredient.name not in ingredients:
                    ingredients[ingredient.name] = {
                        'amount': 0,
                        'measurement_unit': ingredient.measurement_unit
                    }
                ingredients[ingredient.name]['amount'] += amount
        ingredients = sorted(ingredients.items(), key=lambda v: v[0])
        result = []
        for i, ingredient in enumerate(ingredients, start=1):
            result.append(
                f'{i}. {ingredient[0]} ({ingredient[1]["measurement_unit"]})'
                f' — {ingredient[1]["amount"]}.'
            )
        result = '\n'.join(result)
        return HttpResponse(result.encode())
