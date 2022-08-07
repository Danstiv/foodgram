from django.db import models
from django_filters import rest_framework as filters

from .models import Ingredient, Recipe, Tag


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(method='custom_search_filter')

    class Meta:
        model = Ingredient
        fields = ['name']

    def custom_search_filter(self, queryset, name, value):
        q1_expr = {name + '__istartswith': value}
        q2_expr = {name + '__icontains': value}
        queryset = queryset.filter(
            models.Q(**q1_expr) | models.Q(**q2_expr)
        ).annotate(
            is_important=models.ExpressionWrapper(
                models.Q(**q1_expr),
                output_field=models.BooleanField()
            )
        ).order_by('-is_important')
        return queryset


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(field_name='favorited_by', method='custom_flag_filter')
    is_in_shopping_cart = filters.BooleanFilter(field_name='added_to_shopping_cart_by', method='custom_flag_filter')
    author = filters.NumberFilter(field_name='author_id')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = [
            'is_favorited', 'is_in_shopping_cart',
            'author', 'tags',
        ]

    def custom_flag_filter(self, queryset, name, value):
        if not value:
            return queryset
        if not self.request.user.is_authenticated:
            return queryset.none()
        return queryset.filter(**{name: self.request.user})
