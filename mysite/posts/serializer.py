from rest_framework import serializers
from .models import Post, Comment, Comments

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('type', 'author', 'comment', 'contentType', 'published', 'id')


class CommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)
    class Meta:
        model = Comments
        fields = ('type', 'page', 'size', 'post', 'id', 'comments')

class PostSerializer(serializers.ModelSerializer):
    commentsSrc = CommentsSerializer()
    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 
            'author', 'categories', 'count', 'comments', 'commentsSrc', 'published', 'visibility', 'unlisted')
