from django.db import models

# Create your models here.

class Author(models.Model):
    type = "author"
    id = models.CharField(max_length=200, primary_key=True)
    url = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    displayName = models.CharField(max_length=200)
    github = models.CharField(max_length=200)
    profileImage = models.CharField(max_length=200)
    following = models.ManyToManyField('self', symmetrical=False)

# class FollowRequest(models.Model):
#     type = "Follow"
#     summary = models.CharField(max_length=200)
#     # the sender may not exist in the reciever's db
#     actor = models.JSONField()
#     object = models.ForeignKey(Author, on_delete=models.CASCADE)

