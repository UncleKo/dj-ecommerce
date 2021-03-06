# Generated by Django 2.2.8 on 2021-03-07 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0003_auto_20210301_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='order',
            field=models.IntegerField(default=0, verbose_name='順番'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='other_images', to='core.Item', verbose_name='商品'),
        ),
    ]
