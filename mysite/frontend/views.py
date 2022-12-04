from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from PIL import Image
from inbox.models import Inbox
from authors.models import Author
from authors.serializer import AuthorSerializer
from posts.models import Post, Comment, Comments
from posts.serializer import CommentSerializer
from .forms import PostForm
import uuid
import requests
from requests.auth import HTTPBasicAuth
import json
import commonmark
import base64
import threading
import datetime
from io import BytesIO

LOCAL_NODES = ['127.0.0.1:8000',
               'http://127.0.0.1:8000',
               'http://127.0.0.1:8000/',
               'cmput404f22t17.herokuapp.com/',
               'https://cmput404f22t17.herokuapp.com/',
               'https://cmput404f22t17.herokuapp.com']

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

def threaded_request(url, json_data, username, password):
    # "solution" to heroku app being to slow to return from post endpoint
    # this thread should be run as a 
    try:
        # we don't care about the response for these really so just continue if it takes over
        # 5 seconds
        requests.post(url, json=json_data, auth=HTTPBasicAuth(username, password), timeout=5)
    except Exception:
        pass

def _format_post_data_for_remote(post, remote_url):
    if "socialdistribution-cmput404.herokuapp.com" in remote_url:
        post = {"item": post}
        print(post)
    return post

def send_post_to_inboxs(request, post_json, author_id):
    '''Send newly created post object to relevant inbox
       @param post_json: json representation of post object
       @param author_id: author that is sending the post
                      used to get relevant remote followers
    '''
    post_json = json.loads(post_json)
    author = Author.objects.get(pk=author_id)
    is_local_author = author.host in LOCAL_NODES
    username = None
    password = None
    TEAM_6 = "socialdistribution-cmput404.herokuapp.com"
    if user_data := request.session.get('user_data'):
        username = user_data[0]
        password = user_data[1]
    inboxs = set()
    with requests.Session() as client:
        # set the client auth if relevant session info is present
        # otherwise we just make the requests without
        if username and password:
                client.auth = HTTPBasicAuth(username, password)
        def get_items(req_url):
                    # get request on urls with and without trailing '/'s
                    response = client.get(req_url.strip('/'))
                    if response.status_code >= 400:
                        response = client.get(req_url.strip('/')+'/')
                    return response
        def add_followers():
            # add follower inbox endpoint to inboxs
            resp = get_items(author.url.strip('/')+'/followers')
            if resp.status_code < 400:
                friends = resp.content.decode('utf-8')
                friends = json.loads(friends)
                if type(friends) == dict:
                    followers = friends.get('items')
                    # these followers items should be authors
                    if not followers:
                        return
                    for follower in followers:
                        inboxs.add(follower['url'].strip('/')+'/inbox/')
                elif type(friends) == list:
                    # asummed that this endpoint erroniously returned just a list of authors
                    for follower in friends:
                        inboxs.add(follower['url'].strip('/')+'/inbox/')
        if post_json['visibility'].upper() == "PUBLIC":
            # add all local + remote inboxs to inbox set
            local_authors = Author.objects.all()
            for local_author in local_authors:
                inboxs.add(local_author.url.strip('/')+'/inbox/')
            print("added local authors")
            # and all remote authors on the server that hosts this author
            if not is_local_author and TEAM_6 not in author.host:
                author_resp = get_items(author.host.strip('/')+'/authors')
                if author_resp.status_code < 400:
                    author_resp = author_resp.content.decode('utf-8')
                    remote_authors = json.loads(author_resp)
                    for remote_author in remote_authors['items']:
                        inboxs.add(remote_author['url'].strip('/')+'/inbox/')
            print("added remote authors")
        # add followers to set
        add_followers()
        for url in inboxs:
            post_req_data = _format_post_data_for_remote(post_json, url)
            threading.Thread(target=threaded_request, args=(url, post_req_data, username, password)).start()
        if not is_local_author:
            print("PUTing to remote server", post_json['id'])
            client.put(post_json['id'], json=post_json)
        

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
                post = client.post(post_endpoint, cookies=cookies, data=post_data, headers={'accept':'application/json'})
                print(post.status_code)
                if post.status_code < 400:
                    post = post.content.decode('utf-8')
                    send_post_to_inboxs(request, post, pk)
    return HttpResponseRedirect(home_url)

@permission_classes(IsAuthenticated,)
def comment_submit(request, pk):
    print(request.POST['endpoint'])
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    username = None
    password = None
    if request.session.get('user_data'):
        username = request.session['user_data'][0]
        password = request.session['user_data'][1]

    if request.method == 'POST':
        # remote authors should have a proper representation in our db
        # so we can do this
        print(pk)
        author = Author.objects.get(pk=pk)
        with requests.Session() as client:
            if username and password:
                client.auth = HTTPBasicAuth(username, password)
            comment_data = {
                'author': AuthorSerializer(author).data,
                'comment': request.POST['comment'],
                'published': str(datetime.datetime.now()),
                'id': uuid.uuid4().hex
            }
            headers = {
                'accept': 'application/json'
            }
            comment = client.post(request.POST['endpoint'], headers=headers, json=comment_data)
            print(comment.status_code)
            if comment.status_code < 400:
                comment = json.loads(comment.content.decode('utf-8'))
                inbox_url = request.POST['endpoint'].split('posts/')[0] + 'inbox'
                threaded_request(inbox_url, comment, username, password)
    return HttpResponseRedirect(home_url)


@permission_classes(IsAuthenticated,)
def homepage_view(request, pk):
    url = request.build_absolute_uri().split('home/')[0]
    author = Author.objects.get(pk=url.strip('/').split('/')[-1])
    is_local_user = author.host in LOCAL_NODES
    username = request.session['user_data'][0]
    password = request.session['user_data'][1]
    with requests.Session() as client:
        client.auth = HTTPBasicAuth(username, password)
        url = author.url.strip('/') + '/inbox'
        inbox = client.get(url)
        if not inbox or inbox.status_code >= 400:
            inbox = client.get(url+'/')
        inbox = inbox.content.decode('utf-8')
        inbox = json.loads(inbox)
    # inbox uses a json schema which means updates wont be reflected 
    # here we get the items referenced from their host and replace them in the items box
    removal_list = [] # keep track of indexes of deleted inbox items
    with requests.Session() as client:
        client.auth = HTTPBasicAuth(username, password)
        inbox_items = inbox['items']
        for i in range(len(inbox_items)):
            i_type = inbox_items[i].get('type')
            if not i_type:
                removal_list.append(i)
            # like and comment notifications are less trivial to obtain,
            # and by their nature can probably be left up even if deleted

            # this part is currently causing issues integrating with other groups, 
            # if the other groups post PUT method isn't implemented this causes problems
            """
            if i_type.lower() == 'post' or i_type.lower() == 'comment':
                endpoint = 'id'
                resp = client.get(inbox_items[i][endpoint])
                if resp.status_code >= 400:
                    removal_list.append(i)
                    print(i)
                else:
                    item = resp.content
                    item = item.decode('utf-8')
                    item = json.loads(item)
                    inbox_items[i] = item
            """
            if inbox_items[i]['type'].lower() == 'post':
                # commentSrc is optional so if it is absent we request
                # for the comments from the comments attribute
                resp = client.get(inbox_items[i]['comments'])
                if resp.status_code < 400:
                    comments = resp.content.decode('utf-8')
                    inbox_items[i]['commentsSrc'] = json.loads(comments)
                if inbox_items[i]['contentType'] == 'text/markdown':
                    inbox_items[i]['content'] = commonmark.commonmark(inbox_items[i]['content'])
    removal_list.reverse()
    for i in range(len(removal_list)):
        del inbox_items[removal_list[i]]
    post_form = PostForm()
    return render(request, 'homepage/home.html', {'type': 'inbox', 'items': inbox_items, "post_form": post_form})