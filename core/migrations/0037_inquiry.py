# Generated by Django 2.2.8 on 2020-08-22 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20200822_0142'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=100, null=True, verbose_name='件名(任意)')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='お名前(任意)')),
                ('email', models.EmailField(max_length=254, verbose_name='メールアドレス')),
                ('content', models.TextField(verbose_name='お問い合わせ内容')),
            ],
        ),
    ]