# Generated by Django 4.1.2 on 2022-12-08 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_alter_comment_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='author',
            field=models.JSONField(),
        ),
    ]
