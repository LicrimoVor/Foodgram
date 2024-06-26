# Generated by Django 3.2.3 on 2023-06-15 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'Favorite',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='FollowModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'Follow',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCartModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'ShoppingCart',
                'ordering': ('id',),
            },
        ),
    ]
