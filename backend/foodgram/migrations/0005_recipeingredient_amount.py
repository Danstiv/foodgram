# Generated by Django 2.2.16 on 2022-08-04 16:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0004_auto_20220804_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=False,
        ),
    ]