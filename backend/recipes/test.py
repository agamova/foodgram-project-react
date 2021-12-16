def create(self, validated_data):
    author = validated_data.get('author')
    name = validated_data.get('name')
    if Recipe.objects.filter(author=author, name=name).exists():
        raise exceptions.ValidationError(
            'Рецепт с таким названием уже опубликован вами!'
        )
    cooking_time = validated_data.get('cooking_time')
    if cooking_time <= 0:
        raise exceptions.ValidationError(
            'Укажите корректное время приготовления!'
        )
    tags_data = validated_data.pop('tags')
    ingredients_data = validated_data.pop('ingredients')
    new_recipe = Recipe.objects.create(**validated_data)
    for tag in tags_data:
        tag_object = get_object_or_404(Tag, id=tag.id)
        new_recipe.tags.add(tag_object)
    set_of_id = set()
    for ingredient in ingredients_data:
        id = ingredient.get('id')
        if id not in set_of_id:
            set_of_id.add(id)
            ingredient_object = get_object_or_404(Ingredient, id=id)
            new_recipe.ingredients.add(
                ingredient_object,
                through_defaults={'amount': ingredient.get('amount')}
            )
        else:
            raise exceptions.ValidationError(
                'Ингредиенты должны встречаться в рецепте по одному разу'
            )
    new_recipe.save()
    return new_recipe


def update(self, instance, validated_data):
    instance.author = validated_data.get('author', instance.author)
    instance.name = validated_data.get('name', instance.name)
    instance.cooking_time = validated_data.get(
        'cooking_time',
        instance.cooking_time
    )
    if instance.cooking_time <= 0:
        raise exceptions.ValidationError(
            'Укажите корректное время приготовления!'
        )
    instance.image = validated_data.get('image', instance.image)

    tags_data = validated_data.pop('tags')
    ingredients_data = validated_data.pop('ingredients')
    instance.tags.clear()
    instance.ingredients.clear()
    for tag in tags_data:
        tag_object = get_object_or_404(Tag, id=tag.id)
        instance.tags.add(tag_object)
    set_of_id = set()
    for ingredient in ingredients_data:
        id = ingredient.get('id')
        if id not in set_of_id:
            set_of_id.add(id)
            ingredient_object = get_object_or_404(Ingredient, id=id)
            instance.ingredients.add(
                ingredient_object,
                through_defaults={'amount': ingredient.get('amount')}
            )
        else:
            raise exceptions.ValidationError(
                'Ингредиенты должны встречаться в рецепте по одному разу'
            )
    instance.save()
    return instance


def to_representation(self, instance):
    data = RecipeSerializerForRead(
        instance,
        context=self.context
    ).data

    return data


