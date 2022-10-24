from re import A
from django.http import Http404, HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authors.models import Author
from authors.serializer import AuthorSerializer
from .serializer import LikeCommentSerializer, LikePostSerializer
from .models import Comment, LikeComment, LikePost, Post

# Create your views here.

class PostDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID} 
    def get(self, request, author, pk, format=None):
        # GET [local, remote] get the public post whose id is pk
        pass
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
    def get(self, request, author, format=None):
        # GET [local, remote] get the recent posts from author AUTHOR_ID (paginated)
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

class CommentList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments 
    def get(self, request, author, pk):
        # GET [local, remote] get the list of comments of the post whose id is pk (paginated)
        pass
    def post(self, request, author, pk):
        # POST [local] if you post an object of “type”:”comment”, it will add your comment to the post whose id is pk
        pass

class LikePostList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/likes
    def get(self, request, author_pk, post_pk):
        # GET [local, remote] a list of likes from other authors on AUTHOR_ID’s post POST_ID

        try:
            author = Author.objects.get(pk=author_pk)
            post = author.post_set.get(pk=post_pk)
            likes = LikePost.objects.all().filter(object=post_pk)
            likesData = LikePostSerializer(likes, many=True).data
            return Response(likesData)
        except Post.DoesNotExist:
            return Response('Post doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
        except Author.DoesNotExist:
            return Response('Author doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
        
    
    def post(self, request, author_pk, post_pk):
        try: 
            author = Author.objects.get(pk=author_pk)
            author_display_name = AuthorSerializer(author, many=False).data["displayName"]

            request_copy = request.data.copy()
            request_copy['object'] = f"{post_pk}"
            request_copy['url'] = f"{request.build_absolute_uri('/')}authors/{author_pk}/posts/{post_pk}"
            request_copy['summary'] = f"{author_display_name} likes your post"

            LikePost_Serializer = LikePostSerializer(data=request_copy)
            if LikePost_Serializer.is_valid():
                LikePost_Serializer.save(author=author)
                return Response(LikePost_Serializer.data)
            else:
                return Response(LikePost_Serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Author.DoesNotExist:
            return Response('Author doesn\'t exist', status=status.HTTP_404_NOT_FOUND)


class LikeCommentList(APIView):
    def get(self, request, author_pk, post_pk, comment_pk):
        try:
            author = Author.objects.get(pk=author_pk)
            post = author.post_set.get(pk=post_pk)
            comment = post.comment_set.get(pk=comment_pk)
            likes = LikeComment.objects.all().filter(comment_id=comment_pk)

            likesData = LikeCommentSerializer(likes, many=True).data
            return Response(likesData)
        
        except Author.DoesNotExist:
            return Response('Author doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response('Comment doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response('Post doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
