# Generated by Django 2.2.8 on 2021-03-07 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0004_auto_20210307_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='order',
            field=models.IntegerField(default=99, verbose_name='順番'),
        ),
    ]
