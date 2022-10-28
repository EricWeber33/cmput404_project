from django.contrib import admin

# Register your models here.
from .models import LikeComment, LikePost, Post, Comment, Comments

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Comments)
admin.site.register(LikeComment)
admin.site.register(LikePost)