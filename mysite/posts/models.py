from django.db import models;
from authors.models import Author

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Create your models here.
class Comment(models.Model):
    type = "comment"
    author = models.ForeignKey(
        Author, on_delete=models.DO_NOTHING)
    comment = models.CharField(max_length=200)
    contentType = "text/markdown"
    published = models.DateTimeField(auto_now=True)
    id = models.CharField(max_length=200, primary_key=True)

class Comments(models.Model):
    type = "comments"
    page = models.IntegerField(default=1)
    size = models.IntegerField(default=5)
    post = models.CharField(max_length=200)
    id = models.CharField(max_length=200, primary_key=True)
    comments = models.ManyToManyField(Comment, blank=True)

class Post(models.Model):
    # Content type options
    MARKDOWN = 'text/markdown'
    PLAIN = 'text/plain'
    BASE64 = 'application/base64'
    PNG = 'image/png;base64'
    JPEG = 'image/jpeg;base64'
    CONTENT_TYPES = [
        (MARKDOWN, 'markdown'),
        (PLAIN, 'plain text'),
        (BASE64, 'application/base64'),
        (PNG, 'png'),
        (JPEG, 'jpeg'),
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
    source = models.CharField(blank=True, max_length=200)
    origin = models.CharField(blank=True, max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(
        max_length=50, choices=CONTENT_TYPES, default=PLAIN)
    content = models.TextField()
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, blank=True)
    count = models.IntegerField(default=0)
    comments=models.CharField(max_length=200)
    commentsSrc = models.OneToOneField(Comments, related_name='%(class)s_post', on_delete=models.DO_NOTHING, null=True)
    published = models.DateTimeField(auto_now=True)
    visibility = models.CharField(
        max_length=25, choices=VISIBILITY_CHOICES, default=PUBLIC)
    unlisted = models.BooleanField()
    
class LikePost(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    type = "Like"
    object = models.CharField(max_length=500, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    summary = models.CharField(max_length=500)
    url = models.URLField(max_length=250)

class LikeComment(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    type = "Like"
    object = models.CharField(max_length=500, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    summary = models.CharField(max_length=500)
    url = models.URLField(max_length=250)

