import io

from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import RetrieveListViewSet
from .models import (Ingredient, Favorite, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrAdminOrReadOnlyPermission
from .serializers import (IngredientSerializer, RecipeSerializerForRead,
                          RecipeSerializerForWrite, ShortRecipeSerializer,
                          TagSerializer)

SHOPPING_CART_ADD_ERR_MSG = 'Рецепт уже добавлен в шопинг-лист'
SHOPPING_CART_DELETE_ERR_MSG = 'Рецепт не был добавлен в шопинг-лист'
FAVORITE_ADD_ERR_MSG = 'Рецепт уже добавлен в избранное'
FAVORITE_DELETE_ERR_MSG = 'Рецепт не был добавлен в избранное'


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializerForRead
    permission_classes = (IsAuthorOrAdminOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerForRead
        return RecipeSerializerForWrite

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'GET':
            new, created = ShoppingCart.objects.get_or_create(
                user=user,
                recipe=recipe)
            if not created:
                return Response(
                    {'errors': SHOPPING_CART_ADD_ERR_MSG},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        else:
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                recipe_to_delete = ShoppingCart.objects.get(
                    user=user,
                    recipe=recipe
                )
                recipe_to_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': SHOPPING_CART_DELETE_ERR_MSG},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'GET':
            new, created = Favorite.objects.get_or_create(
                user=user,
                recipe=recipe)
            if not created:
                return Response(
                    {'errors': FAVORITE_ADD_ERR_MSG},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        else:
            if ShoppingCart.objects.filter(user=user,
                                           recipe=recipe).exists():
                recipe_to_delete = Favorite.objects.get(
                    user=user,
                    recipe=recipe
                )
                recipe_to_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': FAVORITE_DELETE_ERR_MSG},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_carts = user.shopping_carts.all()
        recipes = []
        for shopping_cart in shopping_carts:
            recipes.append(shopping_cart.recipe)
        ingredients_objects = dict()
        for recipe in recipes:
            ingredients = RecipeIngredients.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                if name not in ingredients_objects:
                    ingredients_objects[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    ingredients_objects[name]['amount'] += amount
        shopping_list = ''
        for key, value in ingredients_objects.items():
            shopping_list += (f'{key}({value["measurement_unit"]}) - '
                              f'{value["amount"]}\n')
        shopping_list = ingredients_to_pdf(ingredients_objects)
        return FileResponse(
            shopping_list,
            as_attachment=True,
            filename='shopping_list.pdf'
        )


def ingredients_to_pdf(ingredients_dict):
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
    p = canvas.Canvas(buffer)
    p.setFont('DejaVuSerif', 18)
    p.drawString(100, 800, 'Список покупок:')
    p.line(100, 785, 500, 785)
    n = 750
    i = 1
    p.setFont('DejaVuSerif', 14)
    for key, value in ingredients_dict.items():
        p.drawString(
            100,
            n,
            f'{i}. {key}({value["measurement_unit"]}) - {value["amount"]}'
        )
        n -= 20
        i += 1
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
