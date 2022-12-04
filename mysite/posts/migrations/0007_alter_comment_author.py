# Generated by Django 4.1.2 on 2022-12-04 02:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0002_followrequest'),
        ('posts', '0006_remove_comments_page_remove_comments_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authors.author'),
        ),
    ]