# Generated by Django 2.2.8 on 2020-06-24 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_item_inventory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='inventory',
            new_name='stock',
        ),
    ]