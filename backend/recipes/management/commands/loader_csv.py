import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = ('Добавляет данные из csv файла директории /data/ '
            'в базу данных sqlite3. Перед добавлением удаляет все записи '
            'используемой модели!')

    def handle(self, *args, **kwargs):
        with open('/Users/eugenia/Dev/foodgram-project-react/data/ingredients.csv', 'r') as csv_file:
            rows = csv.reader(csv_file, delimiter=',')
            header = ('name', 'measurement_unit')
            Ingredient.objects.all().delete()

            for row in rows:
                object_dict = {key: value for key, value in zip(header, row)}
                Ingredient.objects.get_or_create(**object_dict)