from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.middleware.csrf import get_token
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from PIL import Image
from inbox.models import Inbox
from authors.models import Author
from authors.serializer import AuthorSerializer
from posts.models import Post, Comment, Comments, Like
from posts.serializer import PostSerializer, CommentSerializer, LikeSerializer
from .forms import PostForm
import uuid
import datetime
import requests
from posts.models import Post, Comment, Comments
from posts.serializer import CommentSerializer, PostSerializer
from .forms import PostForm
import uuid
from requests.auth import HTTPBasicAuth
import json
import commonmark
import base64
import threading
import datetime
from io import BytesIO
import aiohttp
import asyncio
import os

on_heroku = 'DYN0' in os.environ
if not on_heroku:
    LOCAL_NODES = ['127.0.0.1:8000',
               'http://127.0.0.1:8000',
               'http://127.0.0.1:8000/']
else:
    LOCAL_NODES = ['cmput404f22t17.herokuapp.com/',
               'https://cmput404f22t17.herokuapp.com/',
               'https://cmput404f22t17.herokuapp.com']

TEAM_6 = "socialdistribution-cmput404.herokuapp.com"
TEAM_9 = "team9-socialdistribution.herokuapp.com"

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
        headers = {"accept":"application/json"}
        res = requests.post(url, json=json_data, headers=headers, auth=HTTPBasicAuth(username, password), timeout=5)
        if res.status_code >= 400:
            requests.post(url.strip('/')+'/', json=json_data, headers=headers, auth=HTTPBasicAuth(username,password), timeout=5)
    except Exception:
        pass

def _format_post_data_for_remote(post, remote_url):
    if TEAM_6 in remote_url:
        post = {"item": post}
    elif post.get('item'):
        post = post['item']
    return post

def send_post_to_inboxs(request, post_json, author_id):
    '''Send newly created post object to relevant inbox
       @param post_json: json representation of post object
       @param author_id: author that is sending the post
                      used to get relevant remote followers
    '''
    post_json = json.loads(post_json)
    author = Author.objects.get(pk=author_id)
    is_local_author = get_current_site(request).domain in author.host
    username = None
    password = None
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
            if TEAM_6 in author.host:
                local_authors = local_authors.exclude(host__contains=TEAM_6)
            for local_author in local_authors:
                inboxs.add(local_author.url.strip('/')+'/inbox/')
            print("added local authors")
            # and all remote authors on the server that hosts this author
            if not is_local_author and not TEAM_6 in author.host:
                author_resp = get_items(author.host.strip('/')+'/authors')
                if author_resp.status_code < 400:
                    author_resp = author_resp.content.decode('utf-8')
                    remote_authors = json.loads(author_resp)
                    for remote_author in remote_authors['items']:
                        inboxs.add(remote_author['url'].strip('/')+'/inbox')
                print("added remote authors")
        # add followers to set
        add_followers()
        for url in inboxs:
            if TEAM_9 in url:
                url = url.replace('/authors', '/service/authors')
            print("sending post to: " + url)
            post_req_data = _format_post_data_for_remote(post_json, url)
            threading.Thread(target=threaded_request, args=(url, post_req_data, username, password)).start()
        if not is_local_author:
            print("PUTing to remote server", post_json['id'])
            url = post_json['id']
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
                # write the image data to the buffer so it can be encoded
                image.save(buffer, format=file_type)
                content = 'data:' + content_type + ',' + \
                    base64.b64encode(buffer.getvalue()).decode('utf-8')
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
def repost_submit(request, pk, post_id):
    author = get_object_from_url(Author, pk)
    post = get_object_from_url(Post, post_id)
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    post_endpoint = url.split('/home/')[0] + "/posts/"
    if request.method == 'POST':
        post_data = PostSerializer(post).data
        post_data['csrfmiddlewaretoken'] = get_token(request)
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
            response = client.post(post_endpoint, cookies=cookies, data=post_data)
            if response.status_code < 400:
                post = response.content.decode('utf-8')
                send_post_to_inboxs(request, post, pk)
                return HttpResponseRedirect(home_url)
            return HttpResponse('Could not repost.', status=response.status_code)

    return HttpResponseRedirect(home_url)

@permission_classes(IsAuthenticated,)
def edit_post(request, pk, post_id):
    author = get_object_from_url(Author, pk)
    post = get_object_from_url(Post, post_id)
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    post_endpoint = url.split('/home/')[0] + "/posts/" + post_id + '/'
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.cleaned_data
            if new_post['image'] is not None:
                image = Image.open(image)
                buffer = BytesIO()
                file_type = 'png'
                if new_post['content_type'] == Post.JPEG:
                    file_type = 'JPEG'
                elif new_post['content_type'] == Post.PNG:
                    file_type = 'PNG'
                else:
                    # supplied an image but didn't say the content type was an image
                    # should this throw an error?
                    pass
                image.save(buffer, format=file_type) # write the image data to the buffer so it can be encoded
                new_post['content'] = 'data:'+ new_post['content_type'] + ',' + base64.b64encode(buffer.getvalue()).decode('utf-8')
            old_post = PostSerializer(post).data
            old_post.update(new_post)
            old_post['csrfmiddlewaretoken'] = get_token(request)
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
                client.post(post_endpoint, cookies=cookies, data=old_post)
    return HttpResponseRedirect(home_url)

@permission_classes(IsAuthenticated,)
def delete_post(request, pk, post_id):
    author = get_object_from_url(Author, pk)
    post = get_object_from_url(Post, post_id)
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    post_endpoint = url.split('/home/')[0] + "/posts/" + post_id + '/'
    if request.method == 'DELETE':
        post_data = PostSerializer(post).data
        post_data['csrfmiddlewaretoken'] = get_token(request)
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
            resp = client.delete(post_endpoint, cookies=cookies, data=post_data)
            if resp.status_code < 400:
                return HttpResponse(status=204)
            else:
                return HttpResponse('Failed to delete post.', status=resp.status_code)

    return HttpResponseRedirect(home_url)


@permission_classes(IsAuthenticated,)
def comment_submit(request, pk):
    url = request.build_absolute_uri()
    redirect_url = url.replace('comment_submit/', '')
    if request.method == 'POST':
        # since remote comments are not part of the spec we can just use the database
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
    return HttpResponseRedirect(redirect_url)

async def get_comments(client, url):
    async with client.get(url) as resp:
        if resp.ok:
            comments = await resp.text()
            comments = json.loads(comments)
            if type(comments) == dict:
                comments = comments.get('comments')
                if comments:
                    return comments
            elif type(comments) == list:
                return comments

async def get_post(client, url):
    async with client.get(url) as resp:
        if resp.ok:
            item = await resp.text()
            item = json.loads(item)
            if item:
                if type(item) == list:
                    item = item[0]
                if type(item) == dict:
                    if not item.get('commentsSrc'):
                        # we need to get the comments src
                        comments_url = item.get('comments')
                        if comments_url:
                            if TEAM_9 in comments_url:
                                comments_url.replace('/authors', '/service/authors')
                            item['commentsSrc'] = await get_comments(client, item['comments'])
                    return item

async def get_posts(urls, username=None, password=None):
    kwargs = {'auth': aiohttp.BasicAuth(username, password)} if username and password else {}
    async with aiohttp.ClientSession(**kwargs) as client:
        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(get_post(client, url)))
        items = await asyncio.gather(*tasks)
        return items

def explore_posts(request, pk):
    url = request.build_absolute_uri()
    home_url = url.replace('/explore', '/home')
    local_url = url.split('/authors')[0] + '/posts/'
    posts = []
    with requests.Session() as client:
        client.headers = {'accept':'application/json'}
        res = client.get(local_url)
        if res.status_code < 400:
            posts.extend(json.loads(res.content.decode('utf-8'))['items'])
        if '127.0.0.1' in local_url:
            # if we are on local host we have to get our actual sites posts as well
            res = client.get('https://cmput404f22t17.herokuapp.com/posts/')
            if res.status_code < 400:
                posts.extend(json.loads(res.content.decode('utf-8'))['items'])
        # add team 18 posts
        res = client.get('https://cmput404team18-backend.herokuapp.com/backendapi/authors/posts/',
                          auth=HTTPBasicAuth('t18user1','Password123!')) 
        if res.status_code < 400:
            posts.extend(json.loads(res.content.decode('utf-8'))['items'])
            # print('team 18 posts added')
        # these will be done with asyncio 
        team_6_authors = client.get('https://socialdistribution-cmput404.herokuapp.com/authors/')
        if team_6_authors.status_code < 400:
            team_6_authors = json.loads(team_6_authors.content.decode('utf-8'))['items']
            urls = [a['url'].strip('/')+'/posts/' for a in team_6_authors]
            t6_posts = asyncio.run(get_posts( urls, username='argho', password='12345678!'))
            posts.extend(t6_posts)
        # team 9 also needs to loop
        team_9_authors = client.get('https://team9-socialdistribution.herokuapp.com/service/authors')
        if team_9_authors.status_code < 400:
            team_9_authors = json.loads(team_9_authors.content.decode('utf-8'))['items']
            urls = [a['url'].replace('/authors', '/service/authors').strip('/')+'/posts/' for a in team_9_authors if TEAM_9 in a]
            t9_posts = asyncio.run(get_posts(urls))
            posts.extend(t9_posts)
        posts = [p for p in posts if p != None]
        for p in posts:
            #print('\n' + p['published'])
            p['raw_content'] = p['content']
            if p['contentType'].lower() == 'text/markdown':
                p['content'] = commonmark.commonmark(p['content'])
        posts = sorted(posts, key=lambda i:i['published'], reverse=True)
    return render(request, 'homepage/explore.html', {'items': posts, 'home_url':home_url})

@permission_classes(IsAuthenticated,)
def homepage_view(request, pk):
    url = request.build_absolute_uri().split('home/')[0]
    explore_url = request.build_absolute_uri().replace('/home', '/explore')
    git_url = request.build_absolute_uri().replace('/home', '/githubactivity')
    author = Author.objects.get(pk=url.strip('/').split('/')[-1])
    is_local_user = author.host in LOCAL_NODES
    is_team_6 = TEAM_6 in author.host
    is_team_9 = TEAM_9 in author.host
    if not request.session.get('user_data'):
        login_url = url.split(pk)[0].replace('authors/', 'login/')
        return HttpResponseRedirect(login_url)
    username = request.session['user_data'][0]
    password = request.session['user_data'][1]
    load_error = False
    try:
        with requests.Session() as client:
            client.auth = HTTPBasicAuth(username, password)
            url = author.url.strip('/') + '/inbox'
            if TEAM_9 in url:
                url = url.replace('/authors', '/service/authors')
            inbox = client.get(url)
            if not inbox or inbox.status_code >= 400:
                inbox = client.get(url+'/')
            inbox = inbox.content.decode('utf-8')
            inbox = json.loads(inbox)
            # print(inbox)
    except Exception as e:
        print('load error', e)
        load_error = True
    # inbox uses a json schema which means updates wont be reflected 
    # here we get the items referenced from their host and replace them in the items box
    removal_list = [] # keep track of indexes of deleted inbox items
    with requests.Session() as client:
        client.auth = HTTPBasicAuth(username, password)
        inbox_items = inbox['items']
        if is_team_6:
            # team 6's inbox is in the opposite order of what we expect
            inbox_items.reverse()
        for i in range(len(inbox_items)):
            i_type = inbox_items[i].get('type')
            if not i_type:
                removal_list.append(i)
            # like and comment notifications are less trivial to obtain,
            # and by their nature can probably be left up even if deleted

            # this part is currently causing issues integrating with other groups, 
            # if the other groups post PUT method isn't implemented this causes problems
            if inbox_items[i]['type'].lower() == 'post':
                # this is how inbox items get updated
                # team 6 post PUT /postlist get seem to not be interacting well
                # so we just take whats in the inbox instead of updating
                if not TEAM_6 in inbox_items[i]['id']:
                    #team 9 specific garbage
                    item_url = inbox_items[i]['id']
                    if TEAM_9 in inbox_items[i]['source']:
                        # team 9's scheme has many issues
                        item_url = f'https://{TEAM_9}/service/authors/{pk}/posts/{inbox_items[i]["id"]}'
                    print(item_url)
                    try:
                        resp = client.get(item_url)
                        if resp.status_code >= 400:
                            removal_list.append(i)
                        else:
                            item = resp.content
                            item = item.decode('utf-8')
                            item = json.loads(item)
                            inbox_items[i] = item
                            # commentSrc is optional so if it is absent we request
                            # for the comments from the comments attribute
                            comments_url = inbox_items[i]['comments']
                            if TEAM_9 in inbox_items[i]['source']:
                                comments_url=item_url+'/comments'
                            resp = client.get(comments_url, headers={"accept":"application/json"})
                            if resp.status_code < 400:
                                comments = resp.content.decode('utf-8')
                                inbox_items[i]['commentsSrc'] = json.loads(comments)
                            # store raw content to allow editing
                            inbox_items[i]['raw_content'] = inbox_items[i]['content']
                            if inbox_items[i]['contentType'] == 'text/markdown':
                                inbox_items[i]['content'] = commonmark.commonmark(inbox_items[i]['content'])
                            inbox_items[i]['like_count'] = Like.objects.filter(
                                object=inbox_items[i]['source']).count()
                            for comment in inbox_items[i]['commentsSrc']["comments"] :
                                comment["like_count"] = Like.objects.filter(
                                    object=inbox_items[i]['commentsSrc']["id"]+comment["id"]+'/').count()
                    except Exception as err:
                        print(err)
                        load_error = True
            elif inbox_items[i]['type'] == "Like":
                if 'comments' in inbox_items[i]['object'] :
                    inbox_items[i]["object_type"] = "comment"
                else:
                    inbox_items[i]["object_type"] = "post"

    removal_list.reverse()
    for i in range(len(removal_list)):
        del inbox_items[removal_list[i]]
    post_form = PostForm()
    return render(request, 'homepage/home.html', {
        'type': 'inbox', 
        'items': inbox_items, 
        "post_form": post_form, 
        'explore_url':explore_url,
        "load_error": load_error,
        "git_url" : git_url,
    })


@permission_classes(IsAuthenticated,)
def like_post_submit(request, pk, post_id):
    
    # postID = post_id.split('/posts/')[1][:-1]
    post = get_object_from_url(Post, post_id)
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    post_like_endpoint = url.split('/home/')[0] + '/posts/'+ post_id + '/likes/'

    if request.method == 'POST':
        with requests.Session() as client:
            client.headers.update(request.headers)
            like_data = {
                "csrfmiddlewaretoken": get_token(request)
            }
            client.headers.update({
                'Content-Type': None,
                'Content-Length': None,
            })
            cookies = {
                'sessionid': request.session.session_key,
                'csrftoken': get_token(request)
            }
            client.post(post_like_endpoint, cookies=cookies, data=like_data)
    
    return HttpResponseRedirect(home_url)



@permission_classes(IsAuthenticated,)
def like_comment_submit(request, pk, comments, comment_id):
    
    comment = get_object_from_url(Comment, comment_id)
    url = request.build_absolute_uri()
    home_url = url.split('/home/')[0] + "/home/"
    comment_like_url = comments + comment_id + '/likes/'
    
    if request.method == 'POST':
        with requests.Session() as client:
            client.headers.update(request.headers)
            like_data = {
                "csrfmiddlewaretoken": get_token(request)
            }
            client.headers.update({
                'Content-Type': None,
                'Content-Length': None,
            })
            cookies = {
                'sessionid': request.session.session_key,
                'csrftoken': get_token(request)
            }
            client.post(comment_like_url, cookies=cookies, data=like_data)
    
    return HttpResponseRedirect(home_url)

@permission_classes(IsAuthenticated,)
def github_activity(request, pk):
    author = get_object_from_url(Author, pk)
    github_name = author.github.split('/')[-1]
    github_events = []
    git_url = f"https://api.github.com/users/{github_name}/events/public"
    url = request.build_absolute_uri()
    home_url = url.split('/githubactivity/')[0] + "/home/"
    
    github_results = requests.get(git_url)
    if github_results.status_code >= 400: 
        return render(request, 'homepage/github.html', {'items': None, 'home_url':home_url})
    github_results = github_results.json()
    for github_post in github_results:
        github_event = {"type": github_post['type'], "repo": github_post['repo']['name'],
                    "time": github_post['created_at']}
        github_events.append(github_event)

    return render(request, 'homepage/github.html', {'items': github_events, 'home_url':home_url})