from xml.etree.ElementTree import Comment
from django.http import Http404, HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializer import CommentSerializer, CommentsSerializer, PostSerializaer

from .models import Post

# Create your views here.

class CommentList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments 
    def get(self, request, author, pk):
        # GET [local, remote] get the list of comments of the post whose id is pk (paginated)
        comments = Post.objects.filter(following__id__in=[pk])
        serializer = CommentsSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, author, pk):
        # POST [local] if you post an object of “type”:”comment”, it will add your comment to the post whose id is pk
        post = Post.objects.filter(following__id__in=[pk])
        serializer = CommentsSerializer(post, data={comments: request.data}, partial=True)
        serializer.save()
        return Response(serializer.data)