from django.contrib import admin

from .models import Author, FollowRequest

admin.site.register(Author)
admin.site.register(FollowRequest)