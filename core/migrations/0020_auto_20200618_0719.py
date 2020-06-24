# Generated by Django 2.2.8 on 2020-06-18 07:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20200612_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingaddress',
            name='primary',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='primary',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_addresses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_time',
            field=models.CharField(blank=True, choices=[('', 'Anytime'), ('A', 'morning'), ('B', '0pm-2pm'), ('C', '2pm-4pm'), ('D', '4pm-6pm'), ('E', '6pm-8pm')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_addresses', to=settings.AUTH_USER_MODEL),
        ),
    ]