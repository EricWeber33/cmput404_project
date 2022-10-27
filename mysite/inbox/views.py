from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import json

from .models import Inbox
from .serializers import InboxSerializer
from posts.serializer import PostSerializer, CommentSerializer
# Create your views here.
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
        except model.DoesNotExist:
            raise Http404
        
class InboxView(APIView):
    
    # URL:://service/authors/{AUTHOR_ID}/inbox
    def get(self, request, pk, format=None):
        """GET [local]: if authenticated get a list of posts sent to AUTHOR_ID (paginated)"""
        url = request.build_absolute_uri().split('inbox')[0]
        inbox = get_object_from_url_or_404(Inbox, url)
        serializer = InboxSerializer(inbox)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        """POST [local, remote]: send a post to the author"""
        url = request.build_absolute_uri().split('inbox')[0]
        inbox = get_object_from_url_or_404(Inbox, url)
        try:
            object_type = request.data['type']
        except KeyError:
            return Response('Unknown type', status=status.HTTP_400_BAD_REQUEST)
        if request.data['type'] == "post":
            if not PostSerializer(data=request.data).is_valid():
                return Response('Invalid post object', status.HTTP_400_BAD_REQUEST)
        elif request.data['type'] == "follow":
            return Response("follow not implemented", status.HTTP_501_NOT_IMPLEMENTED)
        elif request.data['type'] == "like":
            return Response("like not implemented", status.HTTP_501_NOT_IMPLEMENTED)
        elif request.data['type'] == "comment":
            if not CommentSerializer(data=request.data).is_valid():
                return Response('Invalid comment object', status.HTTP_400_BAD_REQUEST)
        else:
            return Response(f'Unsupported object type for inbox: {object_type}', status=status.HTTP_400_BAD_REQUEST)
        inbox.items.insert(0, request.data)
        inbox.save()
        inbox_serializer = InboxSerializer(inbox)
        return Response(inbox_serializer.data)

    def delete(self, request, pk):
        """DELETE [local]: clear the inbox"""
        url = request.build_absolute_uri().split('inbox')[0]
        inbox = get_object_from_url_or_404(Inbox, url)
        inbox.items.clear()
        inbox.save()
        serializer = InboxSerializer(inbox)
        return Response(serializer.data)
        