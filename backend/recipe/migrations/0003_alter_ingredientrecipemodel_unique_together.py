# Generated by Django 3.2.3 on 2023-06-11 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ingredientrecipemodel',
            unique_together={('ingredient', 'recipe')},
        ),
    ]