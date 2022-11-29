from django.forms import CharField
from rest_framework import serializers
from authors.serializer import AuthorSerializer
from .models import Like, Post, Comment, Comments


class CreatePostSerializer(serializers.ModelSerializer):  # Specifies what needs to be given in the creation of a Post
    class Meta:
        model = Post
        fields = ('title', 'description', 'source', 'content', 'contentType',
            'visibility', 'unlisted')

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    author = AuthorSerializer()
    class Meta:
        model = Comment
        fields = ('type', 'author', 'comment', 'contentType', 'published', 'id')


class CommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)
    id = serializers.CharField()
    class Meta:
        model = Comments
        fields = ('type', 'post', 'id', 'comments')

class PostSerializer(serializers.ModelSerializer):
    commentsSrc = CommentsSerializer()
    id = serializers.CharField()
    author = AuthorSerializer()
    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 
            'author', 'categories', 'count', 'comments', 'commentsSrc', 'published', 'visibility', 'unlisted')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if "/" not in ret["id"]:
            ret["id"] = f'{ret["author"]["url"].strip("/")}/posts/{ret["id"]}/'
        return ret

class LikeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    object = serializers.CharField()
    class Meta:
        model = Like
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['@context'] = ret['context']
        ret.pop('context')
        ret.pop('id')
        ret['type'] = 'Like'
        return ret