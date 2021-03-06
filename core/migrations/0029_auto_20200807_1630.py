# Generated by Django 2.2.8 on 2020-08-07 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20200728_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='discount_price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_time',
            field=models.CharField(blank=True, choices=[('', '指定なし'), ('A', '午前中'), ('B', '0pm-2pm'), ('C', '2pm-4pm'), ('D', '4pm-6pm'), ('E', '6pm-8pm')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_option',
            field=models.CharField(blank=True, choices=[('C', 'クレジットカード'), ('B', '銀行振込')], max_length=2, null=True),
        ),
    ]
