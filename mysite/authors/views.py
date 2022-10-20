from django.http import Http404, HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializer import AuthorSerializer

from .models import Author

# Create your views here.

class AuthorList(APIView):
    # URL: ://service/authors/ 
    def get(self, request, format=None):
        # GET [local, remote]: retrieve all profiles on the server (paginated) 
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

class AuthorDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/ 
    def get_object(self, pk):
        try:
            return Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        # GET [local, remote]: retrieve AUTHOR_ID’s profile
        author = self.get_object(pk)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        # POST [local]: update AUTHOR_ID’s profile
        pass

class FollowerList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/followers 
    def get(self, request, pk, format=None):
        # GET [local, remote]: get a list of authors who are AUTHOR_ID’s followers
        followers = Author.objects.filter(following__id__in=[pk])
        serializer = AuthorSerializer(followers, many=True)
        return Response({"type":"followers","items":serializer.data})

class FollowerDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID} 
    def get(self, request, pk, foreign, format=None):
        # GET [local, remote] check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID
        pass

    def put(self, request, pk, foreign, format=None):
        # PUT [local]: Add FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID (must be authenticated)
        pass

    def delete(self, request, pk, foreign, format=None):
        # DELETE [local]: remove FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID
        pass