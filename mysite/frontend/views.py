from http import cookies
from lib2to3.pgen2 import token
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.middleware.csrf import get_token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from PIL import Image
from inbox.models import Inbox
from authors.models import Author
from authors.serializer import AuthorSerializer
from posts.models import Post, Comment, Comments
from posts.serializer import PostSerializer, CommentSerializer
from .forms import PostForm
import uuid
import datetime
import requests 
import json
import commonmark
import base64
from io import BytesIO

LOCAL_NODES = ['127.0.0.1:8000', 'https://cmput404f22t17.herokuapp.com/']

def get_object_from_url(model, url):
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
            return None
        
@permission_classes(IsAuthenticated,)
def post_submit(request, pk):
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    post_endpoint = url.split('/home/')[0] + "/posts/"
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.pop('title')
            description = form.cleaned_data.pop('description')
            content = form.cleaned_data.pop('content')
            content_type = form.cleaned_data.pop('content_type')
            visibility = form.cleaned_data.pop('visibility')
            image = form.cleaned_data.pop('image')
            if image is not None:
                image = Image.open(image)
                buffer = BytesIO()
                file_type = 'png'
                if content_type == Post.JPEG:
                    file_type = 'JPEG'
                elif content_type == Post.PNG:
                    file_type = 'PNG'
                else:
                    # supplied an image but didn't say the content type was an image
                    # should this throw an error?
                    pass
                image.save(buffer, format=file_type) # write the image data to the buffer so it can be encoded
                content = 'data:'+ content_type + ',' + base64.b64encode(buffer.getvalue()).decode('utf-8')
            post_data = {
                "csrfmiddlewaretoken": get_token(request),
                "title": title,
                "description": description,
                "content": content, 
                "contentType": content_type,
                "source": "",
                "visibility": visibility,
                "unlisted": False
            }
            with requests.Session() as client:
                client.headers.update(request.headers)
                client.headers.update({
                    'Content-Type': None,
                    'Content-Length': None,
                    'Cookie': None
                })
                cookies = {
                    'sessionid': request.session.session_key,
                    'csrftoken': get_token(request)
                }
                client.post(post_endpoint, cookies=cookies, data=post_data)
    return HttpResponseRedirect(home_url)
        
@permission_classes(IsAuthenticated,)
def comment_submit(request, pk):
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    if request.method == 'POST':
       
        # TODO use the endpoint instead of the model view
        # attempt at this below
        """
        client = requests.Session()
        author = Author.objects.get(pk=pk)
        author = json.dumps(AuthorSerializer(author).data)
        cookies = {
            'sessionid': request.session.session_key,
            'csrftoken': get_token(request)
            }
        data = {
            'csrfmiddlewaretoken': get_token(request),
            'author': author,
            'comment':request.POST['comment'],
            'published': str(datetime.datetime.now()),
            'id': uuid.uuid4().hex
        }
        client.post(request.POST['endpoint'], cookies=cookies, data=data)
        """
        author = Author.objects.get(pk=pk)
        comment = Comment.objects.create(
            author=author,
            comment=request.POST['comment'],
            id=uuid.uuid4().hex
        )
        comment_src = get_object_from_url(Comments, request.POST['endpoint'])
        if comment_src != None:
            comment_src.comments.add(comment)
        comment.save()
        comment_src.save()
        # send notification to post authors inbox
        recipient_author_inbox = request.POST['endpoint'].split('/posts/')[0]
        inbox = get_object_from_url(Inbox, recipient_author_inbox)
        inbox.items.insert(0, CommentSerializer(comment).data)
        inbox.save()
    return HttpResponseRedirect(home_url)

@permission_classes(IsAuthenticated,)
def homepage_view(request, pk):
    url = request.build_absolute_uri().split('home/')[0]
    author = Author.objects.get(pk=url.strip('/').split('/')[-1])
    is_local_user = author.host in LOCAL_NODES
    if is_local_user:
        inbox = Inbox.objects.get(pk=url)
    else:
        username = request.session['user_data'][0]
        password = request.session['user_data'][1]
        with requests.Session() as client:
            client.headers.update({
                'Authorization': f'Basic {username}:{password}'
            })
            url = author.url.strip('/') + '/' + 'inbox'
            inbox = client.get(url).content
            inbox = inbox.decode('utf-8')
            inbox = json.loads(inbox)
           
    # inbox uses a json schema which means updates wont be reflected 
    # here we get the items referenced from db and replace them in the items box
    removal_list = [] # keep track of indexes of deleted inbox items
    for i in range(len(inbox['items'])):
        if is_local_user:
            if not 'type' in inbox.items[i].keys():
                removal_list.append(i)
            elif inbox.items[i]['type'] == "post":
                try:
                    post = Post.objects.get(pk=inbox.items[i]['id'])
                    inbox.items[i] = PostSerializer(post).data
                    if inbox.items[i]['contentType'] == 'text/markdown':
                        inbox.items[i]['content'] = commonmark.commonmark(inbox.items[i]['content'])
                except Post.DoesNotExist:
                    removal_list.append(i)
            elif inbox.items[i]['type'] == "comment":
                pass
    removal_list.reverse()
    for i in range(len(removal_list)):
        del inbox.items[removal_list[i]]
    if is_local_user:
        inbox.save()
    post_form = PostForm()
    return render(request, 'homepage/home.html', {'type': 'inbox', 'items': inbox['items'], "post_form": post_form})