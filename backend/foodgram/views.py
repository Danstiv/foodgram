from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, RecipeIngredient, Tag
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
    queryset = Recipe.objects.all()
    permission_classes = [IsReadOnlyOrIsAuthor]
    pagination_class = RecipePagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial', False):
            return self.http_method_not_allowed(request)
        return super().update(request, *args, **kwargs)

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
        ingredients = RecipeIngredient.objects.filter(
            recipe__added_to_shopping_cart_by=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(
            total_amount=Sum('amount')
        )
        result = []
        for i, ingredient in enumerate(ingredients, start=1):
            result.append(
                f'{i}. {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' — {ingredient["total_amount"]}.'
            )
        result = '\n'.join(result)
        return HttpResponse(result.encode(), content_type='text/plain')
