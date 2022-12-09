from django.forms import CharField
from rest_framework import serializers
from authors.serializer import AuthorSerializer
from .models import Like, Post, Comment, Comments


class UpdatePostSerializer(serializers.ModelSerializer):  #Returns what has been updated in the creation of a Post
    class Meta:
        model = Post
        fields = ('title', 'description', 'content', 'contentType',
            'visibility', 'unlisted')

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    author = AuthorSerializer()
    class Meta:
        model = Comment
        fields = ('type', 'author', 'comment', 'contentType', 'published', 'id')
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            comment = Comment.objects.get(id=ret['id'])
            comment_src = Comments.objects.all().filter(comments=comment)
            ret['id'] = comment_src[0].post.strip('/') + '/comments/' + ret['id'] +'/'
        finally:
            return ret

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

class PostListSerializer(serializers.Serializer):
    type = serializers.CharField()
    items = PostSerializer(many=True)

class LikeSerializer(serializers.ModelSerializer):
    object = serializers.CharField()
    class Meta:
        model = Like
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['@context'] = ret['context']
        ret.pop('context')
        ret['type'] = 'Like'
        ret.pop('id')
        return ret