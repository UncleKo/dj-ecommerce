# Generated by Django 2.2.8 on 2020-07-28 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20200727_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='shipped',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]