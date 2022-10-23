from rest_framework import serializers
from .models import Author
from .models import Comment, Comments

'''
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('type', 'author', 'post', 'comment', 'contentType', 'published', 'id')
'''

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ('type', 'page', 'size', 'post', 'id', 'comment')
