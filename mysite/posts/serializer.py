from django.forms import CharField
from rest_framework import serializers
from .models import LikePost, LikeComment, Post, Comment, Comments

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 
            'author', 'categories', 'count', 'comments', 'published', 'visibility', 'unlisted')

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    class Meta:
        model = Comment
        fields = ('type', 'author', 'comment', 'contentType', 'published', 'id')


class CommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)
    id = serializers.CharField()
    class Meta:
        model = Comments
        fields = ('type', 'page', 'size', 'post', 'id', 'comments')

class PostSerializer(serializers.ModelSerializer):
    commentsSrc = CommentsSerializer()
    id = serializers.CharField()
    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 
            'author', 'categories', 'count', 'comments', 'commentsSrc', 'published', 'visibility', 'unlisted')

class LikeCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikeComment
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['object'] = ret['url']
        ret.pop('url')
        return ret

class LikePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikePost
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['object'] = ret['url']
        ret.pop('url')
        return ret
