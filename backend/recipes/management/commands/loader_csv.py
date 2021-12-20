import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = ('Добавляет данные из csv файлов директории /data/ '
            'в базу данных. Перед добавлением удаляет все записи '
            'используемой модели!')

    def handle(self, *args, **kwargs):
        with open('data/ingredients.csv', 'r') as csv_file:
            rows = csv.reader(csv_file, delimiter=',')
            header = ('name', 'measurement_unit')
            Ingredient.objects.all().delete()

            for row in rows:
                object_dict = {key: value for key, value in zip(header, row)}
                Ingredient.objects.get_or_create(**object_dict)

        with open('data/tags.csv', 'r') as csv_file:
            rows = csv.reader(csv_file, delimiter=',')
            header = ('name', 'color', 'slug')
            Tag.objects.all().delete()

            for row in rows:
                object_dict = {key: value for key, value in zip(header, row)}
                Tag.objects.get_or_create(**object_dict)
