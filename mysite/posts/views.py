from pydoc import visiblename
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializer import PostSerializer, CreatePostSerializer
from .models import Post
from authors.models import Author

import uuid

# Create your views here.

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
    serializer_class = CreatePostSerializer

    def get(self, request, author_id, format=None):
        # GET [local, remote] get the recent posts from author AUTHOR_ID (paginated)
        author = Author.objects.get(pk=author_id)
        posts = Post.objects.filter(author=author)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, author_id, format=None):
        # POST [local] create a new post but generate a new id
        serializer = self.serializer_class(data=request.data)
        author = Author.objects.get(pk=author_id)
        postIDNew = uuid.uuid4() # create a unique id for the post using the uuid library
        if serializer.is_valid():
            title = serializer.data.get('title')
            description = serializer.data.get('description')
            source = serializer.data.get('source')
            visibility = serializer.data.get('visibility')
            unlisted = serializer.data.get('unlisted')
        
        post = Post(id=postIDNew, title=title, description=description, source=source, author=author, visibility=visibility, unlisted=unlisted)
        post.save()
        return Response(CreatePostSerializer(post).data, status=200)


class ImageDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/image 
    def get(self, request, author, pk, format=None):
        # GET [local, remote] get the public post converted to binary as an image 
        # return 404 if not an image
        pass

class CommentList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments 
    def get(self, request, author, pk):
        # GET [local, remote] get the list of comments of the post whose id is pk (paginated)
        pass
    def post(self, request, author, pk):
        # POST [local] if you post an object of “type”:”comment”, it will add your comment to the post whose id is pk
        pass