# Generated by Django 3.2.3 on 2023-06-11 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profile_user', '0001_initial'),
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcartmodel',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping', to='recipe.recipemodel', verbose_name='Рецепт'),
        ),
    ]