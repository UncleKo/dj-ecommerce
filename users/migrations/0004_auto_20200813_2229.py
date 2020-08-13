# Generated by Django 2.2.8 on 2020-08-13 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200813_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='city',
            field=models.CharField(max_length=100, verbose_name='市町村'),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='state',
            field=models.CharField(max_length=100, verbose_name='都道府県'),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='street_address',
            field=models.CharField(max_length=100, verbose_name='番地/部屋番号'),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='zip',
            field=models.CharField(max_length=100, verbose_name='郵便番号'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='city',
            field=models.CharField(max_length=100, verbose_name='市町村'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='state',
            field=models.CharField(max_length=100, verbose_name='都道府県'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='street_address',
            field=models.CharField(max_length=100, verbose_name='番地/部屋番号'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='zip',
            field=models.CharField(max_length=100, verbose_name='郵便番号'),
        ),
    ]
