import urllib
import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView



from .forms import LoginForm, RegisterForm
from .models import Author
from inbox.models import Inbox
from .serializer import AuthorSerializer

# Create your views here.

class AuthorList(APIView):
    permission_classes = (IsAuthenticated,)
    # URL: ://service/authors/ 
    def get(self, request, format=None):
        print(request.user)
        # GET [local, remote]: retrieve all profiles on the server (paginated) 
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

class AuthorDetail(APIView):
    permission_classes = (IsAuthenticated,)
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
    permission_classes = (IsAuthenticated,)
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

def login_view(request):
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
                        return HttpResponseRedirect('/authors/{}/'.format(urllib.parse.quote(user.author.id, safe='')))
                form.add_error('Server Admin has not verified your account')
            else:
                form.add_error('Could not login that account')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            displayName = form.cleaned_data.pop('displayName')
            github = form.cleaned_data.pop('github')
            profileImage = form.cleaned_data.pop('profileImage', None)
            password = make_password(form.cleaned_data.pop('password1'))
            form.cleaned_data.pop('password2')
            try:
                user = User.objects.create(**form.cleaned_data, password=password)
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
    logout(request)
    return HttpResponseRedirect('/login/')