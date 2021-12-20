from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredients, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Represents the model Ingredient in admin interface."""
    list_display = ('id', 'name', 'measurement_unit')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Represents the model Tag in admin interface."""
    list_display = ('id', 'name', 'color', 'slug')


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    """Represents the model RecipeIngredient in admin interface."""
    list_display = ('id', 'recipe', 'ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Represents the model Recipe in admin interface."""
    list_display = ('id',
                    'name',
                    'get_tags',
                    'get_ingredients',
                    'text',
                    'image',
                    'author',
                    'cooking_time'
                    )

    def get_tags(self, obj):
        return '\n'.join([str(p) for p in obj.tags.all()])

    def get_ingredients(self, obj):
        return '\n'.join([str(p) for p in obj.ingredients.all()])
