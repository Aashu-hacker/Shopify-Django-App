# Generated by Django 3.2.3 on 2021-06-04 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0003_order_is_tagged'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='raw_data',
            field=models.JSONField(default=dict),
        ),
    ]
