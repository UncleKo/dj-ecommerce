# Generated by Django 2.2.8 on 2020-07-28 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20200728_0705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='shipped',
        ),
        migrations.AddField(
            model_name='order',
            name='shipped',
            field=models.BooleanField(default=False),
        ),
    ]
