# Generated by Django 4.1.2 on 2022-10-25 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inbox', '0002_alter_inbox_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inbox',
            name='items',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
