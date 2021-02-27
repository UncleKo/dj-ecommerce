# Generated by Django 2.2.6 on 2020-06-04 05:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0006_auto_20191111_0219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='photos.Category', verbose_name='カテゴリー(option)'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='origin',
            field=models.ImageField(upload_to='photos/%y/%m/', verbose_name='画像'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='posts', to='photos.Tag', verbose_name='タグ(option)'),
        ),
    ]
