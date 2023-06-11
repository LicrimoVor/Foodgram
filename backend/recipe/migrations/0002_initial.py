# Generated by Django 3.2.3 on 2023-06-11 12:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipe', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='recipemodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AddField(
            model_name='recipemodel',
            name='ingredients',
            field=models.ManyToManyField(through='recipe.IngredientRecipeModel', to='recipe.IngredientModel', verbose_name='Ингрендиенты'),
        ),
        migrations.AddField(
            model_name='recipemodel',
            name='tags',
            field=models.ManyToManyField(through='recipe.TagRecipeModel', to='recipe.TagModel', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='ingredientrecipemodel',
            name='ingredient',
            field=models.ForeignKey(default='Какой то ингредиент', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='ingredient_recipe', to='recipe.ingredientmodel', verbose_name='Ингредиент (id)'),
        ),
        migrations.AddField(
            model_name='ingredientrecipemodel',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipe', to='recipe.recipemodel', verbose_name='Рецепт (id)'),
        ),
        migrations.AlterUniqueTogether(
            name='ingredientmodel',
            unique_together={('name', 'measurement_unit')},
        ),
    ]
