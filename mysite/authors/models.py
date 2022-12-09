from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Author(models.Model):
    type = "author"
    id = models.CharField(max_length=200, primary_key=True)
    url = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    displayName = models.CharField(max_length=200)
    github = models.CharField(blank=True, max_length=200)
    profileImage = models.CharField(blank=True, max_length=200)
    following = models.JSONField(default=list)

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True)
    verified = models.BooleanField(default=False)


class FollowRequest(models.Model):
    # actor wants to follow object
    # should be in object's inbox
    summary = models.CharField(max_length=500)
    type = "Follow"
    actor = models.JSONField(default=dict)
    object = models.JSONField(default=dict)
