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


from .forms import LoginForm, RegisterForm
from .models import Author, FollowRequest
from inbox.models import Inbox
from .serializer import AuthorSerializer, FollowRequestSerializer

# Create your views here.


class AuthorList(APIView):
    permission_classes = (IsAuthenticated,)
    # URL: ://service/authors/

    def get(self, request, format=None):
        '''
        Description:
        Gets all profiles on the server

        Params:
        request: request

        Returns:
        Response containing all profiles
        '''
        print(request.user)

        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)


class AuthorDetail(APIView):
    permission_classes = (IsAuthenticated,)
    # URL: ://service/authors/{AUTHOR_ID}/

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
    permission_classes = (IsAuthenticated,)
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
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    return HttpResponseRedirect('/authors/')
                if hasattr(user, 'author'):
                    if user.author.verified:
                        login(request, user)
                        return HttpResponseRedirect('/authors/{}/home/'.format(urllib.parse.quote(user.author.id, safe='')))
                form.add_error('Server Admin has not verified your account')
            else:
                form.add_error('Could not login that account')
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
                scheme = request.scheme
                user_url = scheme + '://' + domain + '/authors/'+user_id+'/'
                author = Author.objects.create(
                    id=user_id,
                    url=user_url,
                    host=domain,
                    displayName=displayName,
                    github=github,
                    profileImage=profileImage,
                    user=user
                )
                inbox = Inbox.objects.create(author=user_url)
                user.save()
                author.save()
                inbox.save()
                return HttpResponseRedirect('/login/')
            except Exception as e:
                print(e)
                form.add_error('Could not create account')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


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
