from django.db import models;
from authors.models import Author

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    # Content type options
    MARKDOWN = 'text/markdown'
    PLAIN = 'text/plain'
    BASE64 = 'application/base64'
    PNG = 'image/png;base64'
    JPEG = 'image/jpeg;base64'
    CONTENT_TYPES = [
        (MARKDOWN, 'text/markdown'),
        (PLAIN, 'text/plain'),
        (BASE64, 'application/base64'),
        (PNG, 'image/png;base64'),
        (JPEG, 'image/jpeg;base64'),
    ]

    # Visibility options
    PUBLIC = 'PUBLIC'
    FRIENDS = 'FRIENDS'
    VISIBILITY_CHOICES = [
        (PUBLIC, 'Public'),
        (FRIENDS, 'Friends'),
    ]

    type = "post"
    title = models.CharField(max_length=200)
    id = models.CharField(max_length=200, primary_key=True)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(
        max_length=50, choices=CONTENT_TYPES, default=PLAIN)
    content = models.TextField()
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    count = models.IntegerField()
    comments = models.CharField(max_length=200)
    published = models.DateTimeField(auto_now=True)
    visibility = models.CharField(
        max_length=25, choices=VISIBILITY_CHOICES, default=PUBLIC)
    unlisted = models.BooleanField()


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