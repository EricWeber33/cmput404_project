# Generated by Django 4.1.2 on 2022-10-26 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_alter_comments_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='comments',
            field=models.ManyToManyField(blank=True, null=True, to='posts.comment'),
        ),
    ]
