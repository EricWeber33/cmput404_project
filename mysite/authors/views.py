import urllib
import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .forms import LoginForm, RegisterForm, RemoteRegisterForm
from .models import Author, FollowRequest
from inbox.models import Inbox
import requests
from requests.auth import HTTPBasicAuth
import json
import base64
from .serializer import AuthorSerializer, AuthorListSerializer, FollowRequestSerializer

from rest_framework import permissions

class AuthenticatePut(permissions.BasePermission):        

    def has_permission(self, request, view):
        if request.method == 'GET' or request.method == 'DELETE':
            return True
        return request.user and request.user.is_authenticated

# Create your views here.


class AuthorList(APIView):
    # URL: ://service/authors/
    serializer_class = AuthorListSerializer

    def get(self, request, format=None):
        '''
        Description:
        Gets all profiles on the server

        Params:
        request: request

        Returns:
        Response containing all profiles
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
        authors = Author.objects.all().order_by('-id')
        data = AuthorSerializer(authors, many=True).data
        data = {'type':'authors', 'items':data}
        if paginated:
            try:
                page_index = (page-1)*page_size
                last_index = min(page_index+page_size, len(data['items']))
                data['items'] = data['items'][page_index:last_index]
            except Exception:
                return Response("Internal error", status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not AuthorListSerializer(data=data).is_valid():
            return Response("Internal error", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data)


class AuthorDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/
    serializer_class = AuthorSerializer

    def get_object(self, pk):
        '''
        Description:
        Attempts to get an author

        Params:
        pk: String 
            pk of an Author

        Returns:
        Returns an author but if not found then raise 404
        '''
        try:
            return Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        '''
        Description: 
        Gets an author

        Params:
        request: request
        pk: String 
            pk of an Author

        Returns:
        Returns response containing author (if it was found)
        '''
        author = self.get_object(pk)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        # POST [local]: update AUTHOR_ID’s profile
        pass


class FollowerList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/followers

    def get(self, request, pk, format=None):
        '''
        Description:
        Get a list of authors who are following an author

        Params:
        request: request
        pk: String 
            pk of an Author

        Returns:
        Returns response containing the followers
        '''

        followers = Author.objects.filter(following__id__in=[pk])
        serializer = AuthorSerializer(followers, many=True)
        return Response({"type": "followers", "items": serializer.data})


class MakeFollowRequest(APIView):
    serializer_class = FollowRequestSerializer
    def post(self, request, author_id):
        '''
        Description:
        Creates a follow request from the authenticated author to another author.

        Params:
        request: request
        author_id: String 

        Returns:
        Returns response containing if the follow request was successfully created. 
        '''

        if not request.user.is_authenticated:
            return Response("You are not authenticated. Log in first", status=status.HTTP_401_UNAUTHORIZED)

        else:

            object_author = get_object_or_404(Author, pk=author_id)
            author = get_object_or_404(Author, pk=request.user.author.id)

            if author == object_author:
                return Response("You cannot follow yourself!", status=status.HTTP_403_FORBIDDEN)

            else:
                follow_request = FollowRequest.objects.create(
                    summary=f"{author.displayName} wants to follow {object_author.displayName}",
                    actor=author,
                    object=object_author
                )
                follow_request.save()

                follow_serializer = FollowRequestSerializer(follow_request)

                # send the request to object authors inbox
                object_author_inbox = Inbox.objects.get(
                    author=object_author.url)
                object_author_inbox.items.insert(0, follow_serializer.data)
                object_author_inbox.save()

                return Response(follow_serializer.data)


class FollowerDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
    permission_classes = (AuthenticatePut,)
    def get(self, request, author_id, foreign_author_id):
        '''
        Description:
        Checks if a foreign author is a following an author

        Params:
        request: request
        author_id: String
        foreign_author_id: String   

        Returns:
        Returns response containing if the foreign author follows the author or not, or HTTP_404_NOT_FOUND if either author do not exist
        '''

        current = get_object_or_404(Author, pk=author_id)
        foreign = get_object_or_404(Author, pk=foreign_author_id)

        if current in foreign.following.all():
            return Response(f"{foreign.displayName} follows {current.displayName}")
        else:
            return Response(f"{foreign.displayName} does not follow {current.displayName}")

    def put(self, request, author_id, foreign_author_id):
        '''
        Description:
        Adds a foreign author as a follower of an author, who must be authenticated.

        Params:
        request: request
        author_id: String
        foreign_author_id: String   

        Returns:
        Returns response containing if the follower was successfully added. 
        '''

        current = get_object_or_404(Author, pk=author_id)
        foreign = get_object_or_404(Author, pk=foreign_author_id)

        # only authenticated users can approve their own follow requests
        if not request.user.is_authenticated or current.id != request.user.author.id:
            return Response("You are not allowed to perform this action.", status=status.HTTP_401_UNAUTHORIZED)
        else:
            followerSet = FollowRequest.objects.all().filter(
                object=current, actor=foreign)

            # check if a follow request exists to approve, else do not add follower
            if len(followerSet) != 0:
                foreign.following.add(current)
                return Response(f"Success. {foreign.displayName} follows you.")

            else:
                return Response(f"Follow request from {foreign.displayName} doesn't exist", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, author_id, foreign_author_id):
        # DELETE [local]: remove FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID
        '''
        Description:
        Deletes a foreign author as a follower of an author. Either author must be authenticated.

        Params:
        request: request
        author_id: String
        foreign_author_id: String   

        Returns:
        Returns response if the follower was successfully deleted. 
        '''

        current = get_object_or_404(Author, pk=author_id)
        foreign = get_object_or_404(Author, pk=foreign_author_id)

        # only an authenticated author can delete their own follower or unfollow another author
        if foreign.id == request.user.author.id or current.id == request.user.author.id and request.user.is_authenticated:
            if current in foreign.following.all():
                follow_request_set = FollowRequest.objects.all().filter(
                    object=current, actor=foreign)
                for follow_request in follow_request_set:
                    follow_request.delete()

                foreign.following.remove(current)

                return Response(f"{foreign.displayName} unfollowed {current.displayName} successfully")

            else:
                return Response(f"Cannot perform this action. {foreign.displayName} does not follow {current.displayName}")

        else:
            return Response("You are not allowed to perform this action.", status=status.HTTP_401_UNAUTHORIZED)


def login_view(request):
    '''
    Description:
    Attempts to log a user in

    Params:
        request: request

    Returns:
    A render for login
    '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # This is probably a security vulnerability
            request.session['user_data'] = [username, password]
            request.session.save()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    return HttpResponseRedirect('/authors/')
                if hasattr(user, 'author'):
                    if user.author.verified:
                        login(request, user)
                        return HttpResponseRedirect('/authors/{}/home/'.format(urllib.parse.quote(user.author.id, safe='')))
                form.add_error(None, 'Server Admin has not verified your account. Login is avalible only once your account has been verified.')
            else:
                form.add_error(None, 'Could not login into that account')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def register_view(request):
    '''
    Description:
    Upon registration creates a user and it's associated objects

    Params:
        request: request

    Returns:
    A render for registration
    '''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        remote_form = RemoteRegisterForm(request.POST)
        if form.is_valid():
            displayName = form.cleaned_data.pop('displayName')
            github = form.cleaned_data.pop('github')
            profileImage = form.cleaned_data.pop('profileImage', None)
            password = make_password(form.cleaned_data.pop('password1'))
            form.cleaned_data.pop('password2')
            try:
                user = User.objects.create(
                    **form.cleaned_data, password=password)
                user_id = uuid.uuid4().hex
                domain = get_current_site(request).domain
                if domain == "cmput404f22t17.herokuapp.com":
                    domain = "https://" + domain + "/"
                scheme = request.scheme
                user_url = scheme + '://' + domain + '/authors/'+user_id+'/'
                author = Author.objects.create(
                    id=user_id,
                    url=user_url,
                    host=domain,
                    displayName=displayName,
                    github=github,
                    profileImage=profileImage,
                    user=user,
                    verified=True
                )
                inbox = Inbox.objects.create(author=user_url)
                user.save()
                author.save()
                inbox.save()
                return HttpResponseRedirect('/login/')
            except Exception as e:
                print(e)
                form.add_error('Could not create account')
        elif remote_form.is_valid():
            try:
                print(remote_form.cleaned_data)
                initialize_remote_user(remote_form.cleaned_data.pop('remote_author'),
                                       remote_form.cleaned_data.pop('username'),
                                       remote_form.cleaned_data.pop('password'))
                return HttpResponseRedirect('/login/')
            except Exception as e:
                #TODO clean up failed user creation in DB
                raise e
                pass
    else:
        form = RegisterForm()
        remote_form = RemoteRegisterForm();
    return render(request, 'registration/register.html', {'form': form, 'remote_form': remote_form})

def initialize_remote_user(remote_author, username, password):
    host = remote_author.split('/authors/')[0]
    with requests.Session() as client:
        client.auth = HTTPBasicAuth(username, password)
        resp = client.get(remote_author)
        if hasattr(resp, 'data'):
            data = getattr(resp, 'data')
        elif hasattr(resp, 'body'):
            data = getattr(resp, 'body')
        elif hasattr(resp, 'content'):
            data = getattr(resp, 'content')
        else:
            raise Exception("Could not parse author object")
        print(data)
        if type(data) == bytes:
            data = data.decode('utf-8')
        if type(data) == str:
            data = json.loads(data)
        author = make_author(host, data)
        user = User.objects.create(
            username=username,
            password=make_password(password)
        )
        author.user=user
        user.save()
        author.save()

def make_author(host, recieved_author):
    assert type(recieved_author) == dict
    if not recieved_author.get("id"):
        raise Exception("could not parse author object")
    a_id = recieved_author.get("id")
    a_id = a_id.split('/')[-2] if a_id[-1] == '/' else a_id.split('/')[-1]
    a_url = recieved_author.get("url") or f"{host}/authors/{a_id.split('authors/')[-1]}"
    a_host = recieved_author.get("host") or host
    a_displayName = recieved_author.get("displayName") or \
                    recieved_author.get("displayname") or \
                    recieved_author.get("display_name") or \
                    None
    if not a_displayName:
        raise Exception("could not parse author object")
    a_git = recieved_author.get("github") or ""
    a_img = recieved_author.get("profileImage") or "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
    return Author.objects.create(
        id=a_id,
        url=a_url,
        host=a_host,
        displayName=a_displayName,
        github=a_git,
        profileImage=a_img
    )

def logout_view(request):
    '''
    Description:
    Logs user out

    Params:
        request: request

    Return:
    User brought back to inital login page
    '''
    logout(request)
    return HttpResponseRedirect('/login/')
