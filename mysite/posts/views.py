from operator import mod
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializer import PostSerializer, CommentSerializer, CommentsSerializer
from .models import Post, Comments, Comment
from authors.models import Author


def get_object_from_url_or_404(model, url):
    """attempts to return a db item using a url as primary key"""
    try:
        return model.objects.get(pk=url)
    except model.DoesNotExist:
        if url[-1] == '/':
            url = url[:-1]
        else:
            url = url + "/"
        try:
            return model.objects.get(pk=url)
        except model.DoeNotExist:
            raise Http404

class PostDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID} 

    def get(self, request, author_id, postID, format=None):
        # GET [local, remote] get the public post whose id is pk
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def post(self, request, author, pk, format=None):
        # POST [local] update the post whose id is pk (must be authenticated)
        pass
    def put(self, request, author, pk, format=None):
        # PUT [local] create a post where its id is pk
        pass
    def delete(self, request, author, pk, format=None):
        # DELETE [local] remove the post whose id is pk
        pass

class PostList(APIView):
    # URL ://service/authors/{AUTHOR_ID}/posts/ 
    def get(self, request, author_id, format=None):
        # GET [local, remote] get the recent posts from author AUTHOR_ID (paginated)
        author = Author.objects.get(pk=author_id)
        posts = Post.objects.filter(author=author)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

        pass
    def post(self, request, author, format=None):
        # POST [local] create a new post but generate a new id
        pass

class ImageDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/image 
    def get(self, request, author, pk, format=None):
        # GET [local, remote] get the public post converted to binary as an image 
        # return 404 if not an image
        pass


class CommentDetail(APIView):
    def get(self, request, author_id, post_id, comment_id):
        url = request.build_absolute_uri()
        comment = get_object_from_url_or_404(Comment, url)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def post(self, request, auhtor_id, post_id, comment_id):
        pass

class CommentList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments 
    def get(self, request, author_id, post_id):
        # GET [local, remote] get the list of comments of the post whose id is pk (paginated)
        url = request.build_absolute_uri()
        comments = get_object_from_url_or_404(Comments, url)
        serializer = CommentsSerializer(comments)
        return Response(serializer.data)

    def post(self, request, author, pk):
        # POST [local] if you post an object of “type”:”comment”, it will add your comment to the post whose id is pk
        pass
