from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Author(models.Model):
    type = "author/"
    id = models.CharField(max_length=200, primary_key=True)
    url = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    displayName = models.CharField(max_length=200)
    github = models.CharField(blank=True, max_length=200)
    profileImage = models.CharField(blank=True, max_length=200)
    following = models.ManyToManyField('self', blank=True, symmetrical=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.displayName
class FollowRequest(models.Model):
    summary = models.CharField(max_length=500)
    type = "Follow"
    actor = models.ForeignKey(
        Author, on_delete=models.CASCADE, unique=False, related_name="follower")
    object = models.ForeignKey(
        Author, on_delete=models.CASCADE)
