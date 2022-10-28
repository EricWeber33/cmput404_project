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
    following = models.ManyToManyField('self', blank=True, symmetrical=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True)
    verified = models.BooleanField(default=False)

# class FollowRequest(models.Model):
#     #  actor is sending a request to object
#     type = "Follow"
#     summary = models.CharField(max_length=200)
#     # the sender may not exist in the reciever's db
#     actor = models.JSONField()
#     object = models.ForeignKey(Author, on_delete=models.CASCADE)

