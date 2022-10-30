from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from inbox.models import Inbox
from posts.models import Post
from posts.serializer import PostSerializer
from .forms import PostForm
import uuid
import requests


@permission_classes(IsAuthenticated,)
def post_submit(request, pk):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.pop('title')
            description = form.cleaned_data.pop('description')
            content = form.cleaned_data.pop('content')
            content_type = form.cleaned_data.pop('content_type')
            visibility = form.cleaned_data.pop('visibility')
            post_endpoint = request.build_absolute_uri().split('/home/')[0] + "/posts/"
            post_id = uuid.uuid4().hex
            while len(Post.objects.filter(pk=post_id)) < 1:
                post_id = uuid.uuid4().hex
            post = {
                "type": post,
                "title": title,
                "id": post_id,
                "description": description,
                ""
            }
    return homepage_view(request, pk)
            

@permission_classes(IsAuthenticated,)
def homepage_view(request, pk):
    url = request.build_absolute_uri().split('home/')[0]
    inbox = Inbox.objects.get(pk=url)
    # inbox uses a json schema which means updates wont be reflected 
    # here we get the items referenced from db and replace them in the items box
    for i in range(len(inbox.items)):
        if inbox.items[i]['type'] == "post":
            post = Post.objects.get(pk=inbox.items[i]['id'])
            inbox.items[i] = PostSerializer(post).data
        elif inbox.items[i]['type'] == "comment":
            pass
        inbox.save()
    form = PostForm()
    return render(request, 'homepage/home.html', {'type': inbox.type, 'items': inbox.items, "form": form})