# Generated by Django 4.1.2 on 2022-10-20 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=200)),
                ('host', models.CharField(max_length=200)),
                ('displayName', models.CharField(max_length=200)),
                ('github', models.CharField(max_length=200)),
                ('profileImage', models.CharField(max_length=200)),
            ],
        ),
    ]