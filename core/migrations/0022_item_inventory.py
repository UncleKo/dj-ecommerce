# Generated by Django 2.2.8 on 2020-06-24 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20200623_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='inventory',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]