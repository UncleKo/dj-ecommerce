# Generated by Django 2.2.8 on 2020-06-12 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20200611_1535'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='apartment_address',
            new_name='city',
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='state',
            field=models.CharField(default='CA', max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_time',
            field=models.CharField(blank=True, choices=[('N', 'Anytime'), ('A', 'morning'), ('B', '0pm-2pm'), ('C', '2pm-4pm'), ('D', '4pm-6pm'), ('E', '6pm-8pm')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_option',
            field=models.CharField(blank=True, choices=[('C', 'Credit Card'), ('B', 'Bank Transfer')], max_length=2, null=True),
        ),
    ]