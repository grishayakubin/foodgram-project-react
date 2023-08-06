from django.contrib import admin
from .models import (Favorite, Follow, Ingredient, IngredientContained, Recipe,
                     ShoppingList, Tag)

EMPTY = '-пусто-'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientContained


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = (IngredientRecipeInline,)
    empty_value_display = EMPTY


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'is_favorited',
        'amount_favorites', 'amount_tags', 'amount_ingredients'
    )
    search_fields = ('author', 'name', 'tags')
    inlines = (IngredientRecipeInline,)
    empty_value_display = EMPTY

    def is_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    is_favorited.short_description = 'В избранном'

    @staticmethod
    def amount_favorites(obj):
        return obj.favorites.count()

    amount_favorites.short_description = 'Количество избранных'

    @staticmethod
    def amount_tags(obj):
        return "\n".join([i[0] for i in obj.tags.values_list('name')])

    amount_tags.short_description = 'Теги'

    @staticmethod
    def amount_ingredients(obj):
        return "\n".join([i[0] for i in obj.ingredients.values_list('name')])

    amount_ingredients.short_description = 'Ингредиенты'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = EMPTY


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('user', )
    empty_value_display = EMPTY


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user', )
    empty_value_display = EMPTY
