# Generated by Django 3.1.6 on 2021-02-16 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_voucher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voucher',
            name='code',
            field=models.CharField(max_length=15),
        ),
    ]
