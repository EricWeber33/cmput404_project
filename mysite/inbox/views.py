from django.http import HttpResponse, Http404
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
import commonmark

import json

from .models import Inbox
from .serializers import InboxSerializer
from authors.serializer import FollowRequestSerializer
from posts.serializer import PostSerializer, CommentSerializer, LikeSerializer


from rest_framework import permissions


class IsPostOrIsAuthenticated(permissions.BasePermission):        

    def has_permission(self, request, view):
        if request.method == 'POST' or request.method == 'DELETE':
            return True
        return request.user and request.user.is_authenticated

# Create your views here.
def get_object_from_url_or_404(model, url):
    '''
    Description:
    Attempts to return an item from the db using a url as the primary key

    Params:
    model: model
        Model object
    url: String
        Url to specific location
    
    Returns:
    Either teturns the item if found otherwise if not found raise Http404
    '''
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
    permission_classes = (IsPostOrIsAuthenticated,)
    # URL:://service/authors/{AUTHOR_ID}/inbox
    def get(self, request, pk, format=None):
        '''
        Description:
        Get a list of posts sent to authors inbox. Must be authenticated.

        Params:
        request: request
        pk: String 
            pk of an Author

        Returns:
        Inbox which contains posts
        '''

        if paginated := 'page' in request.GET.keys():
            page = request.GET.get('page')
            page_size = request.GET.get('size') or 5
            try:
                page = int(page)
                page_size = int(page_size)
                assert page > 0
                assert page_size > 0
            except Exception:
                return Response("Bad query", status.HTTP_400_BAD_REQUEST)
        url = request.build_absolute_uri().split('inbox')[0]
        inbox = get_object_from_url_or_404(Inbox, url)
        serializer = InboxSerializer(inbox)
        data = serializer.data
        if paginated:
            try:
                page_index = (page-1)*page_size
                last_index = min(page_index+page_size, len(data['items']))
                data['items'] = data['items'][page_index:last_index]
            except Exception:
                return Response("Internal error", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data)

    def post(self, request, pk, format=None):
        '''
        Description:
        Send a post to authors inbox

        Params:
        request: request
        pk: String 
            pk of an Author

        Returns:
        Response which has post added to the inbox
        '''
        url = request.build_absolute_uri().split('inbox')[0]
        inbox = get_object_from_url_or_404(Inbox, url)
        try:
            object_type = request.data['type']
        except KeyError:
            return Response('Unknown type', status=status.HTTP_400_BAD_REQUEST)
        if request.data['type'] == "post":
            if not PostSerializer(data=request.data).is_valid():
                return Response('Invalid post object', status.HTTP_400_BAD_REQUEST)
        elif request.data['type'] == "Follow":
            if not FollowRequestSerializer(data=request.data).is_valid():
                return Response('Invalid follow request', status.HTTP_400_BAD_REQUEST)
        elif request.data['type'] == "Like":
            # Due to some issues with serializing this is more involved than the other
            # there is likely a better way to do this but this 'works'
            if '@context' in request.data.keys():
                request.data['context'] = request.data['@context']
                request.data.pop('@context')
            if not LikeSerializer(data=request.data).is_valid():
                return Response('Invalid like object', status.HTTP_400_BAD_REQUEST)
            request.data['@context'] = request.data['context']
            request.data.pop('context')
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
        '''
        Description:
        Clears inbox of all items

        Params:
        request: request
        pk: String 
            pk of an Author

        Returns:
        Response with inbox that has been cleared
        '''
        url = request.build_absolute_uri().split('inbox')[0]
        inbox = get_object_from_url_or_404(Inbox, url)
        inbox.items.clear()
        inbox.save()
        serializer = InboxSerializer(inbox)
        return Response(serializer.data)
        