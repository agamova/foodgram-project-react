# Generated by Django 2.2.16 on 2021-12-13 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20211212_1012'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeIngredient',
            new_name='RecipeIngredients',
        ),
    ]
