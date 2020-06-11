# Generated by Django 2.2.8 on 2020-06-11 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20200610_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_time',
            field=models.CharField(blank=True, choices=[('A', 'morning'), ('B', '0pm-2pm'), ('C', '2pm-4pm'), ('D', '4pm-6pm'), ('E', '6pm-8pm')], max_length=2, null=True),
        ),
    ]
