from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authors.models import Author
from authors.serializer import AuthorSerializer
from .models import Comment, Comments, Like, Post
from django.db.models import Q
from .serializer import PostSerializer, UpdatePostSerializer, CommentSerializer, CommentsSerializer, LikeSerializer
from .models import Post, Comments, Comment
from inbox.models import Inbox
from authors.models import Author
import uuid
import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import threading
from rest_framework import permissions

LOCAL_NODES = ['127.0.0.1:8000',
               'http://127.0.0.1:8000',
               'http://127.0.0.1:8000/',
               'cmput404f22t17.herokuapp.com/',
               'https://cmput404f22t17.herokuapp.com/',
               'https://cmput404f22t17.herokuapp.com']

def threaded_request(url, json_data, username, password):
    # "solution" to heroku app being to slow to return from post endpoint
    # this thread should be run as a 
    try:
        # we don't care about the response for these really so just continue if it takes over
        # 5 seconds
        requests.post(url, json=json_data, auth=HTTPBasicAuth(username, password), timeout=5)
    except Exception:
        pass

class AuthenticatePost(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        return True


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
    Either returns the item if found otherwise if not found raise Http404
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

class PostDetail(APIView):
    permission_classes = (AuthenticatePost,)
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}
    def get(self, request, author_id, postID, format=None):
        '''
        Description:
        Gets the public post whose id is the primary key

        Params:
        request: request
        author_id: String
        postID: String

        Returns:
        Response containing the post
        '''
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def post(self, request, author_id, postID, format=None): # WIP (cannot handle an incomplete HTML form)
        '''
        Description:
        Updates the post whose id is pk. Must be authenticated.

        Params:
        request: request
        author_id: String
        postID: String

        Returns:
        Response with an updated post and a status code of 200
        '''
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        data = request.data
        # Fetch data
        try:
            post.title = data.get('title', post.title)
            post.description = data.get('description', post.description)
            post.content = data.get('content', post.content)
            post.visibility = data.get('visibility', post.visibility)
            post.unlisted = data.get('unlisted', post.unlisted)
            post.save()
            return Response(UpdatePostSerializer(post).data, status=200)
        except:
            return Response('POST was unsuccessful. Please check the required information was filled out correctly again.', status=204)

    def put(self, request, author_id, postID, format=None):
        # PUT [local] create a post where its id is pk
        serializer = self.serializer_class(data=request.data)
        author = Author.objects.get(pk=author_id)
        url = request.build_absolute_uri(f'/authors/{author_id}/posts/{postID}')
        if serializer.is_valid():  # fetch fields
            title = serializer.data.get('title')
            description = serializer.data.get('description')
            content = serializer.data.get('content')
            contentType = serializer.data.get('contentType')
            visibility = serializer.data.get('visibility') #PUBLIC OR FRIENDS
            unlisted = serializer.data.get('unlisted')
            comments = f'{url}/comments'
            commentsSrc = Comments.objects.create(
                post= url,
                id=f'{url}/comments'
            )
            # Create post object
            post = Post.objects.create(
                id=postID,
                title=title,
                description=description,
                origin=url,
                content=content,
                contentType=contentType,
                author=author,
                comments=comments,
                commentsSrc=commentsSrc,
                visibility=visibility,
                unlisted=unlisted)
            post.save()
            return Response(PostSerializer(post).data, status=200)
        return Response('Put was unsuccessful. Please check the required information was filled out correctly again.', status=422)


    def delete(self, request, author_id, postID, format=None):
        '''
        Description:
        Deletes the post whose id is pk

        Params:
        request: request
        author_id: String
        postID: String

        Returns:
        A response with status 200 and a message indicating post has been successfully deleted
        '''
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        post.delete()
        return Response('Post deleted successfully.', status=200)


class PostList(APIView):
    # URL ://service/authors/{AUTHOR_ID}/posts/

    def get(self, request, author_id, format=None):
        '''
        Description:
        Gets recent posts from an author

        Params:
        request: request
        author_id: String

        Returns:
        Response containing the posts
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
        author = Author.objects.get(pk=author_id)
        posts = Post.objects.filter(author=author).order_by("-published")
        if paginated:
            page_index = (page-1)*page_size
            last_index = min(page_index+page_size, len(posts))
            posts = posts[page_index:last_index]
        data = PostSerializer(posts, many=True).data
        data = {'type':'posts', 'items':data}
        return Response(data)

    def _format_post_data_for_remote(self, post, remote_url):
        if "socialdistribution-cmput404.herokuapp.com" in remote_url:
            post = {"item": post}
            print(post)
        return post

    def post(self, request, author_id, format=None):
        '''
        Description:
        Creates a new post that contains a newly generated id

        Params:
        request: request
        author_id: String

        Returns:
        Response containing the new post with a status code of 200. If failed a message indicating
        failure will be sent instead with a status code of 204
        '''
        author = Author.objects.get(pk=author_id)
        is_local_author = author.host in LOCAL_NODES
        url = author.url.strip('/') + '/posts/'
        serializer = self.serializer_class(data=request.data)
        
        postIDNew = uuid.uuid4()  # create a unique id for the post using the uuid library
        if serializer.is_valid():  # fetch fields
            title = serializer.data.get('title')
            description = serializer.data.get('description')
            source = f'{url}{postIDNew}/'
            content = serializer.data.get('content')
            contentType = serializer.data.get('contentType')
            visibility = serializer.data.get('visibility') #PUBLIC OR FRIENDS
            unlisted = serializer.data.get('unlisted')
            comments = f'{url}{postIDNew}/comments/'
            commentsSrc = Comments.objects.create(
                post=f'{url}{postIDNew}/',
                id=f'{url}{postIDNew}/comments/'
            )
            # Create post object
            post = Post.objects.create(
                id=postIDNew,
                title=title,
                description=description,
                source=source,
                origin=source,
                content=content,
                contentType=contentType,
                author=author,
                comments=comments,
                commentsSrc=commentsSrc,
                visibility=visibility,
                unlisted=unlisted)
            post.save()
            post_data = PostSerializer(post).data
            print("Saved post in DB")
            # The following sends the newly created post to every relevant inbox
            # ideally this would be extracted to a differnent method and there
            # would be some utility that calls this endpoint then does this with
            # the new post, but this will do for now
            username = None
            password = None
            if user_data := request.session.get('user_data'):
                username = user_data[0]
                password = user_data[1]
            with requests.Session() as client:
                # set the client auth if relevant session info is present
                # otherwise we just make the requests without
                if username and password:
                    client.auth = HTTPBasicAuth(username, password)

                inboxs = set() # set containing urls for all relevant inbox endpoints

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
                            for follower in followers:
                                inboxs.add(follower['url'].strip('/')+'/inbox/')
                        elif type(friends) == list:
                            # asummed that this endpoint erroniously returned just a list of authors
                            for follower in friends:
                                inboxs.add(follower['url'].strip('/')+'/inbox/')
        
                if visibility.upper() == 'FRIENDS':
                    add_followers()
                elif visibility.upper() == 'PUBLIC':
                    add_followers()
                    print('added followers')
                    # besides followers we need to get all local authors
                    # this can be done more easily through the db with less risk of
                    # errors. Note local authors in this case includes registered
                    # remote authors on this server
                    local_authors = Author.objects.all()
                    for local_author in local_authors:
                        inboxs.add(local_author.url.strip('/')+'/inbox/')
                    print("added local authors")
                    # and all remote authors on the server that hosts this author
                    if not is_local_author:
                        author_resp = get_items(author.host.strip('/')+'/authors')
                        if author_resp.status_code < 400:
                            author_resp = author_resp.content.decode('utf-8')
                            remote_authors = json.loads(author_resp)
                            for remote_author in remote_authors['items']:
                                inboxs.add(remote_author['url'].strip('/')+'/inbox/')
                    print("added remote authors")
                # post the post to all the relevant inbox's
                for url in inboxs:
                    post_req_data = self._format_post_data_for_remote(post_data, url)
                    threading.Thread(target=threaded_request, args=(url, post_req_data, username, password)).start()
                if not is_local_author:
                    print("PUTing to remote server", post_data['id'])
                    #TODO for team 6 this doesn't put but does cause it to be posted to everyones inbox again
                    #client.put(post_data['id'], json=post_data)
            return Response(PostSerializer(post).data, status=200)
        return Response('Post was unsuccessful. Please check the required information was filled out correctly again.', status=422)


class ImageDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/image 
    def get(self, request, author_id, postID, format=None):
        '''
        Description:
        Gets a public post that is converted to binary as an image

        Params:
        request: request
        author_id: String
        postID: String

        Returns:
        Returns the image or 404 if image was not found
        '''
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        if post.contentType not in [Post.JPEG, Post.PNG]:
            return Response(status=404)
        return Response(post.content)


class CommentDetail(APIView):
    def get(self, request, author_id, post_id, comment_id):
        '''
        Description:
        Gets a comment on a specific post

        Params:
        request: request
        author_id: String
        post_id: String
        comment_id: String

        Returns:
        Returns a response containing the comment
        '''
        url = request.build_absolute_uri()
        comment = get_object_from_url_or_404(Comment, url)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def post(self, request, author_id, post_id, comment_id):
        # POST [local] update a comment
        pass


class CommentList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments
    def get(self, request, author_id, post_id):
        '''
        Description:
        Gets the list of comments from a post

        Params:
        request: request
        author_id: String
        post_id: String

        Returns:
        Response containing the list of comments
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
        url = request.build_absolute_uri().split('?')[0] # trim off query params
        comments = get_object_from_url_or_404(Comments, url)
        comments.comments.set(comments.comments.order_by('published'))
        data = CommentsSerializer(comments).data
        if paginated:
            try:
                page_index = (page-1)*page_size
                last_index = min(page_index+page_size, len(data['comments']))
                data['comments'] = data['comments'][page_index:last_index]
                data['page'] = page
                data['size'] = page_size
            except Exception:
                return Response("Internal error", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data)

    def post(self, request, author_id, post_id, format=None):
        '''
        Description:
        Adds a comment to a post whose id is the primary key

        Params:
        request: request
        author_id: String
        post_id: String

        Returns:
        Response after comment has been added
        '''
        url = request.build_absolute_uri()
        data_copy = request.data.copy()
        comments_list = get_object_from_url_or_404(Comments, url)
        if not CommentSerializer(data=data_copy).is_valid():
            return Response('Invalid comment object', status=status.HTTP_400_BAD_REQUEST)
        comment_single = Comment(
            author=Author.objects.get(pk=request.data['author']['id']),
            comment=request.data['comment'],
            published=request.data['published'],
            id=request.data['id'])
        comments_list.comments.add(comment_single)
        comments_list.save()
        comments_serializer = CommentsSerializer(comments_list)
        return Response(comments_serializer.data)

class LikePostList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/likes

    def get(self, request, author_pk, post_pk):
        '''
        Description:
        Gets a list of likes from other authors on an authors specific post

        Params:
        request: request
        author_pk: String
        post_pk: String

        Returns:
        Returns response containing the likes on a post or HTTP_404_NOT_FOUND if either author or post does not exist
        '''
        uri = request.build_absolute_uri().split("/likes")[0]
        other_uri = uri[:-1] if uri[-1] == '/' else uri + '/'
        author = get_object_or_404(Author, pk=author_pk)
        post = get_object_or_404(Post, pk=post_pk, author=author)
        likes = Like.objects.all().filter(Q(object=uri) | Q(object=other_uri))
        likesData = LikeSerializer(likes, many=True).data
        return Response(likesData)
     

    def post(self, request, author_pk, post_pk):
        '''
        Description:
        Post a like from an authenticated author to a post

        Params:
        request: request
        author_pk: String
        post_pk: String

        Returns:
        Returns a response with the like added
        '''
        if request.user.is_authenticated:

            author = Author.objects.get(pk=request.user.author.id)
            author_display_name = AuthorSerializer(
                author, many=False).data["displayName"]

            like_post = Like(
                context=f"TODO",
                author=author,
                summary=f"{author_display_name} likes your post",
                object=f"{request.build_absolute_uri('/')}authors/{author_pk}/posts/{post_pk}"
            )

            like_post.save()
            like_post_serializer = LikeSerializer(like_post)
            return Response(like_post_serializer.data)


class LikeCommentList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}/likes

    def get(self, request, author_pk, post_pk, comment_pk):
        '''
        Description:
        Gets a list of likes on an authors comment

        Params:
        request: request
        author_pk: String
        post_pk: String
        comment_pk: String

        Returns:
        Returns response containing the likes on a comment or HTTP_404_NOT_FOUND if author, post, or comment does not exist
        '''
        uri = request.build_absolute_uri().split("/likes")[0]
        other_uri = uri[:-1] if uri[-1] == '/' else uri + '/'
        author = get_object_or_404(Author, pk=author_pk)
        post = get_object_or_404(Post, pk=post_pk, author=author)
        comment = get_object_from_url_or_404(Comment, uri)
        likes = Like.objects.all().filter(Q(object=uri) | Q(object=other_uri))
        likesData = LikeSerializer(likes, many=True).data
        return Response(likesData)


    def post(self, request, author_pk, post_pk, comment_pk):
        '''
        Description:
        Post a like from the authenticated author to a comment

        Params:
        request: request
        author_pk: String
        post_pk: String
        comment_pk: String

        Returns:
        Returns a response with added like on comment
        '''

        if request.user.is_authenticated:

            author = Author.objects.get(pk=request.user.author.id)
            author_display_name = AuthorSerializer(
                author, many=False).data["displayName"]

            like_comment = Like(
                context = "TODO",
                author=author,
                summary=f"{author_display_name} likes your comment",
                object=f"{request.build_absolute_uri('/')}authors/{author_pk}/posts/{post_pk}/comments/{comment_pk}"
            )

            like_comment.save()
            like_comment_serializer = LikeSerializer(like_comment)
            return Response(like_comment_serializer.data)


class AuthorLikesList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/liked
    def get(self, request, author_pk):
        '''
        Description:
        Gets a list of things the author has liked

        Params:
        request: request
        author_pk: String

        Returns:
        Returns response containing authors likes or if author does not exisst then status of 404
        '''
        try:
            author = Author.objects.get(pk=author_pk)

            likes = Like.objects.all().filter(author=author)
            likes_data = LikeSerializer(likes, many=True).data

            #TODO hide "friends only likes" from non-authenticated authors
            finalData = {"type": "liked",
                         "items": likes_data}
            return Response(finalData)

        except Author.DoesNotExist:
            return Response('Author doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
