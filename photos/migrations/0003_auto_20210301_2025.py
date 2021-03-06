# Generated by Django 2.2.8 on 2021-03-01 11:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0002_photo_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='other_images', to='core.Item', verbose_name='その他画像'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='origin',
            field=models.ImageField(upload_to='other_images/', verbose_name='画像'),
        ),
    ]
