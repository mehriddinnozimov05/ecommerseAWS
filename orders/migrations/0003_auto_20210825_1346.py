# Generated by Django 3.2.6 on 2021-08-25 08:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210824_0219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order_product',
            name='color',
        ),
        migrations.RemoveField(
            model_name='order_product',
            name='size',
        ),
    ]