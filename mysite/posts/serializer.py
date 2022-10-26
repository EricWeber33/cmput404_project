from rest_framework import serializers
from .models import Post
from .models import Comment

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 
            'author', 'categories', 'count', 'comments', 'published', 'visibility', 'unlisted')

class CreatePostSerializer(serializers.ModelSerializer):  # Specifies what needs to be given in the creation of a Post
    class Meta:
        model = Post
        fields = ('title', 'description', 'source', 'content',
            'visibility', 'unlisted')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        field = ('type', 'author', 'post', 'comment', 'contentType', 'published', 'id')