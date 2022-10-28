from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from inbox.models import Inbox
from posts.models import Post
from posts.serializer import PostSerializer

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

    return render(request, 'homepage/home.html', {'type': inbox.type, 'items': inbox.items})