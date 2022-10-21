from django.db import models
from authors.models import Author
from posts.models import Post
from django.contrib.postgres.fields import ArrayField
# Create your models here.
class Inbox(models.Model):
    type = "inbox"
    author = models.CharField(max_length=200, primary_key=True)
    items = models.JSONField(default=list, blank=True)