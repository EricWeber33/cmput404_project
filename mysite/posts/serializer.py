from rest_framework import serializers
from .models import LikePost, LikeComment
from .models import Post
from .models import Comment

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 
            'author', 'categories', 'count', 'comments', 'published', 'visibility', 'unlisted')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        field = ('type', 'author', 'post', 'comment', 'contentType', 'published', 'id')

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