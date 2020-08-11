# Generated by Django 2.2.8 on 2020-08-11 12:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0029_auto_20200807_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='fav_users',
            field=models.ManyToManyField(blank=True, null=True, related_name='fav_items', to=settings.AUTH_USER_MODEL),
        ),
    ]
