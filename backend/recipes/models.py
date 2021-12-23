from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext as _

from .validators import is_convertible_to_color

User = get_user_model()

INGREDIENT_AMOUNT_ERR_MSG = 'Количество ингредиента должно быть больше нуля.'
COOKING_TIME_ERR_MSG = ('Время приготовления пищи не может быть менее одной '
                        'минуты.')


class Tag(models.Model):
    name = models.CharField('Название', max_length=25, unique=True)
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7,
        unique=True,
        validators=(is_convertible_to_color, )
    )
    slug = models.SlugField('Слаг', unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=30)

    def __str__(self):
        return f'{self.name},{self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        'Название',
        max_length=200,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Описание'
    )
    tags = models.ManyToManyField(
        Tag,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(code=1, message=_(COOKING_TIME_ERR_MSG)),

        ]
    )

    def __str__(self):
        return f'{self.name} от  {self.author}'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField(
        'Количество ингредиента',
        validators=[MinValueValidator(
            code=0,
            message=_(INGREDIENT_AMOUNT_ERR_MSG
                      )
        ),
        ]
    )

    class Meta:
        constraints = (models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_ingredient_in_recipe'
        ),
        )

    def __str__(self):
        return (f'В {self.recipe} ингредиент {self.ingredient} в кол-ве '
                f'{self.amount}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    def __str__(self):
        return f'{self.user} likes {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
