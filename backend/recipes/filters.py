import django_filters

from .models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        lookup_expr='exact'
    )
    is_favorited = django_filters.NumberFilter(method='favorited_filter')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return queryset

    def shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset
