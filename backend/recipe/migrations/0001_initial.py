# Generated by Django 3.2.3 on 2023-06-12 08:02

import core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название ингридиента')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Ед. измерения')),
            ],
            options={
                'db_table': 'Ingredient',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(validators=[core.validators.validate_amount_more_zero], verbose_name='Кол-во ингредиента')),
            ],
            options={
                'db_table': 'Recipe-Ingredient',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='RecipeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название рецепта', max_length=200, verbose_name='Название')),
                ('text', models.TextField(help_text='Описание рецепта', verbose_name='Описание')),
                ('image', models.ImageField(upload_to='recipe/image/', verbose_name='Фото блюда')),
                ('cooking_time', models.IntegerField(help_text='Время приготовления в минутах', validators=[core.validators.validate_min_time], verbose_name='Время (мин.)')),
            ],
            options={
                'db_table': 'Recipe',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='TagModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название тега', max_length=200, unique=True, verbose_name='Название')),
                ('color', models.CharField(help_text='Цвет в HEX-формате', max_length=7, unique=True, validators=[core.validators.validate_hex], verbose_name='Цвет')),
                ('slug', models.SlugField(help_text='Slug тега', max_length=200, unique=True, verbose_name='Slug')),
            ],
            options={
                'db_table': 'Tag',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='TagRecipeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_recipe', to='recipe.recipemodel', verbose_name='Рецепт (id)')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_recipe', to='recipe.tagmodel', verbose_name='Тег (id)')),
            ],
            options={
                'db_table': 'Recipe-Tag',
                'ordering': ('id',),
            },
        ),
    ]
