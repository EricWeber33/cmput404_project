from django.contrib import admin

# Register your models here.
from .models import Like, Post, Comment, Comments

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Comments)
admin.site.register(Like)