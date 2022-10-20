from django.db import models

# Create your models here.

class Post(models.Model):
    type = "post"
    title = models.CharField(max_length=200)
    id = models.CharField(max_length=200, primary_key=True)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(max_length=20)
    content = models.TextField()
    author = models.JSONField()
    categories = models.JSONField() # separate table for categories?
    count = models.IntegerField()
    comments = models.CharField(max_length=200)
    published = models.DateTimeField()
    visibility = models.CharField(max_length=200) # textChoices?
    unlisted = models.BooleanField()


class Comment(models.Model):
    type = "comment",
    author = models.JSONField()
    comment = models.CharField(max_length=200)
    contentType = "text/markdown"
    published = models.DateTimeField()
    id = models.CharField(max_length=200, primary_key=True)