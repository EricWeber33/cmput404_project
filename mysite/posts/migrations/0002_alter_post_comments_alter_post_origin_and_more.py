# Generated by Django 4.1.2 on 2022-10-26 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("authors", "0003_alter_author_following"),
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="comments",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="post",
            name="origin",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="post",
            name="source",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.CreateModel(
            name="LikePost",
            fields=[
                (
                    "id",
                    models.CharField(max_length=200, primary_key=True, serialize=False),
                ),
                ("object", models.CharField(max_length=500, null=True)),
                ("summary", models.CharField(max_length=500)),
                ("url", models.URLField(max_length=250)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="authors.author"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LikeComment",
            fields=[
                (
                    "id",
                    models.CharField(max_length=200, primary_key=True, serialize=False),
                ),
                ("object", models.CharField(max_length=500, null=True)),
                ("summary", models.CharField(max_length=500)),
                ("url", models.URLField(max_length=250)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="authors.author"
                    ),
                ),
            ],
        ),
    ]
