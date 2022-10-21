from django.db import models
from authors.models import Author
from post.models import Post

# Create your models here.

class Comment(models.Model):
    type = "comment",
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    contentType = "text/markdown"
    published = models.DateTimeField(auto_now=True)
    id = models.CharField(max_length=200, primary_key=True)

class Comments(models.Model):
    type = "comments",
    page = models.IntegerField;
    size = models.IntegerField;
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE)
    id = models.CharField(max_length=200, primary_key=True)
    comment = models.ManyToManyField(
        Comment, on_delete=models.CASCADE)