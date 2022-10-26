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
    serializer_class = CreatePostSerializer

    def get(self, request, author_id, postID, format=None):
        # GET [local, remote] get the public post whose id is pk
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def post(self, request, author_id, postID, format=None):
        # POST [local] update the post whose id is pk (must be authenticated)
        serializer = self.serializer_class(data=request.data)
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        # Fetch data
        if serializer.is_valid():
            title = serializer.data.get('title')
            description = serializer.data.get('description')
            source = serializer.data.get('source')
            content = serializer.data.get('content')
            visibility = serializer.data.get('visibility')
            unlisted = serializer.data.get('unlisted')     
            # Update Post
            if title != '' or None: post.title = title
            if description != ''or None: post.description = description
            if source != ''or None: post.source = source
            if content != ''or None: post.content = content
            if visibility != ''or None: post.visibility = visibility
            if unlisted != ''or None: post.unlisted = unlisted
            post.save()
            return Response(CreatePostSerializer(post).data, status=200)
        return Response(status=204)


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
        if serializer.is_valid(): # fetch fields
            title = serializer.data.get('title')
            description = serializer.data.get('description')
            source = serializer.data.get('source')
            content = serializer.data.get('content')
            visibility = serializer.data.get('visibility')
            unlisted = serializer.data.get('unlisted')
            # Create post object
            post = Post(id=postIDNew, title=title, description=description, source=source, content=content, author=author, visibility=visibility, unlisted=unlisted)
            post.save()
            return Response(CreatePostSerializer(post).data, status=200)
        return Response('Post was unsuccessful. Please check the required information was filled out correctly again.', status=204)



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