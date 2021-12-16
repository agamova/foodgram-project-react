from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers

from .models import (Ingredient, Favorite, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)
from users.models import Follow, User
from users.serializers import CustomUserSerializer


RECIPE_NAME_ERR_MSG = 'Рецепт с таким названием уже опубликован вами'
RECIPE_COOKING_TIME_ERR_MSG = 'Укажите корректное время приготовления!'
RECIPE_INGREDIENTS_ERR_MSG = ('Нельзя указывать один и тот же ингредиент более'
                              ' одного раза')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializerForRead(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    ingredient = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'ingredient', 'measurement_unit', 'amount')


class RecipeIngredientsSerializerForWrite(serializers.ModelSerializer):
    amount = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'amount'
        ]


class RecipeSerializerForRead(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientsSerializerForRead(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeSerializerForWrite(serializers.ModelSerializer):
    ingredients = RecipeIngredientsSerializerForWrite(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ('ingredients',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time',
                  'author'
                  )

    def validate_name(self, name):
        author = self.context['request'].user
        if Recipe.objects.filter(name=name, author=author).exists():
            raise exceptions.ValidationError(RECIPE_NAME_ERR_MSG)
        return name

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise exceptions.ValidationError(RECIPE_COOKING_TIME_ERR_MSG)
        return cooking_time

    def validate_ingredients(self, ingredients):
        set_of_ingredients_id = set()
        for ingredient in ingredients:
            if ingredient['id'] in set_of_ingredients_id:
                raise exceptions.ValidationError()
            set_of_ingredients_id.add(ingredient['id'])
        return ingredients

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        new_recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            id = tag.id
            tag_object = get_object_or_404(Tag, id=id)
            new_recipe.tags.add(tag_object)
        for ingredient in ingredients_data:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_object = get_object_or_404(Ingredient, id=id)
            new_recipe.ingredients.add(
                ingredient_object,
                through_defaults={'amount': amount}
            )
        new_recipe.save()
        return new_recipe

    def update(self, instance, validated_data):
        instance.author = validated_data.get('author')
        instance.name = self.initial_data.get('name')
        if Recipe.objects.filter(
                name=instance.name,
                author=instance.author
        ).exists():
            raise exceptions.ValidationError(RECIPE_NAME_ERR_MSG)
        instance.cooking_time = validated_data.get('cooking_time')
        instance.image = validated_data.get('image')
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.ingredients.clear()
        for tag in tags_data:
            id = tag.id
            tag_object = get_object_or_404(Tag, id=id)
            instance.tags.add(tag_object)
        for ingredient in ingredients_data:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_object = get_object_or_404(Ingredient, id=id)
            instance.ingredients.add(
                ingredient_object,
                through_defaults={'amount': amount}
            )
        return instance

    def to_representation(self, instance):
        serializer_data = RecipeSerializerForRead(
            instance,
            context=self.context
        ).data
        return serializer_data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeUserSerializer(serializers.ModelSerializer):
    """Represents serializer for following users."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user,
                                     following=obj).exists()

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit is None:
            recipes = obj.recipes.all()
        else:
            recipes = obj.recipes.all()[:int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
