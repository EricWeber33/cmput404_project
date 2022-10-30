from urllib import response
from django.shortcuts import render
from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.test import APIClient
from inbox.models import Inbox
from posts.models import Post
from posts.serializer import PostSerializer
from .forms import PostForm

@permission_classes(IsAuthenticated,)
def post_submit(request, pk):
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    post_endpoint = url.split('/home/')[0] + "/posts/"
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.pop('title')
            description = form.cleaned_data.pop('description')
            content = form.cleaned_data.pop('content')
            content_type = form.cleaned_data.pop('content_type')
            visibility = form.cleaned_data.pop('visibility')
            post_data = {
                "title": title,
                "description": description,
                "content": content, 
                "source": "",
                "visibility": visibility,
                "unlisted": False
            }
            client = APIClient()
            if request.user.is_authenticated:
                client.force_authenticate(request.user)
            client.post(post_endpoint, post_data)
    return HttpResponseRedirect(home_url)
            

@permission_classes(IsAuthenticated,)
def homepage_view(request, pk):
    url = request.build_absolute_uri().split('home/')[0]
    inbox = Inbox.objects.get(pk=url)
    # inbox uses a json schema which means updates wont be reflected 
    # here we get the items referenced from db and replace them in the items box
    removal_list = [] # keep track of indexes of deleted inbox items
    for i in range(len(inbox.items)):
        if not 'type' in inbox.items[i].keys():
            removal_list.append(i)
        elif inbox.items[i]['type'] == "post":
            try:
                post = Post.objects.get(pk=inbox.items[i]['id'])
                inbox.items[i] = PostSerializer(post).data
            except Post.DoesNotExist:
                removal_list.append(i)
        elif inbox.items[i]['type'] == "comment":
            pass
    removal_list.reverse()
    for i in range(len(removal_list)):
        del inbox.items[removal_list[i]]
    inbox.save()
    form = PostForm()
    return render(request, 'homepage/home.html', {'type': inbox.type, 'items': inbox.items, "form": form})