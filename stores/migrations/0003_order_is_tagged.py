# Generated by Django 3.2.3 on 2021-06-04 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0002_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_tagged',
            field=models.BooleanField(default=False),
        ),
    ]
