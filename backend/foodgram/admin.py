from django.contrib import admin

from .models import Ingredient, Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'author',
        'favorited_count',
    ]
    list_filter = ['author', 'name', 'tags']

    def favorited_count(self, obj):
        return obj.favorited_by.count()
    favorited_count.short_description = 'Добавлено в избранное'
    favorited_count.admin_order_field = '-favorited_by__count'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'measurement_unit',
    ]
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'color',
    ]
