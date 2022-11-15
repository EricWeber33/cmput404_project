from pydoc import visiblename

from re import A
from operator import mod
from xmlrpc.client import DateTime
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authors.models import Author
from authors.serializer import AuthorSerializer
from .serializer import LikeCommentSerializer, LikePostSerializer
from .models import Comment, Comments, LikeComment, LikePost, Post

from .serializer import PostSerializer, CreatePostSerializer, CommentSerializer, CommentsSerializer
from .models import Post, Comments, Comment
from inbox.models import Inbox
from authors.models import Author
import json
import uuid


def get_object_from_url_or_404(model, url):
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
            raise Http404


class PostDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}
    serializer_class = CreatePostSerializer

    def get(self, request, author_id, postID, format=None):
        # GET [local, remote] get the public post whose id is pk
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    # WIP (cannot handle an incomplete HTML form)
    def post(self, request, author_id, postID, format=None):
        # POST [local] update the post whose id is pk (must be authenticated)
        serializer = self.serializer_class(data=request.data)
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        # Fetch data
        if serializer.is_valid():
            title = serializer.data.get('title')
            description = serializer.data.get('description')
            source = serializer.data.get('source')
            content = serializer.data.get('content')
            visibility = serializer.data.get('visibility')
            unlisted = serializer.data.get('unlisted')
            # Update Post
            if title != '' and title is not None:
                post.title = title
            if description != '' and description is not None:
                post.description = description
            if source != '' and source is not None:
                post.source = source
            if content != '' and content is not None:
                post.content = content
            if visibility != '' and visibility is not None:
                post.visibility = visibility
            if unlisted != '' and unlisted is not None:
                post.unlisted = unlisted
            post.save()
            return Response(CreatePostSerializer(post).data, status=200)
        return Response(status=204)

    def put(self, request, author, pk, format=None):
        # PUT [local] create a post where its id is pk
        pass

    def delete(self, request, author_id, postID, format=None):
        # DELETE [local] remove the post whose id is pk
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        post.delete()
        return Response('Post deleted successfully.', status=200)


class PostList(APIView):
    # URL ://service/authors/{AUTHOR_ID}/posts/
    serializer_class = CreatePostSerializer

    def get(self, request, author_id, format=None):
        # GET [local, remote] get the recent posts from author AUTHOR_ID (paginated)
        author = Author.objects.get(pk=author_id)
        posts = Post.objects.filter(author=author)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, author_id, format=None):
        # POST [local] create a new post but generate a new id
        url = request.build_absolute_uri()
        serializer = self.serializer_class(data=request.data)
        author = Author.objects.get(pk=author_id)
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
                content=content,
                contentType=contentType,
                author=author,
                comments=comments,
                commentsSrc=commentsSrc,
                visibility=visibility,
                unlisted=unlisted)
            post.save()
            if visibility == 'PUBLIC':
                Inboxs = Inbox.objects.all()
                for inbox in Inboxs:
                    inbox.items.insert(0, PostSerializer(post).data)
                    inbox.save()
            if visibility == 'FRIENDS':
                pass
            return Response(PostSerializer(post).data, status=200)
        return Response('Post was unsuccessful. Please check the required information was filled out correctly again.', status=204)


class ImageDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/image 
    def get(self, request, author_id, postID, format=None):
        # GET [local, remote] get the public post converted to binary as an image 
        # return 404 if not an image
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        if post.contentType not in [Post.JPEG, Post.PNG]:
            return Response(status=404)
        return Response(post.content)


class CommentDetail(APIView):
    def get(self, request, author_id, post_id, comment_id):
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
        # GET [local, remote] get the list of comments of the post whose id is pk (paginated)
        url = request.build_absolute_uri()
        comments = get_object_from_url_or_404(Comments, url)
        serializer = CommentsSerializer(comments)
        return Response(serializer.data)

    def post(self, request, author_id, post_id, format=None):
        # POST [local] if you post an object of “type”:”comment”, it will add your comment to the post whose id is pk
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
        # GET [local, remote] a list of likes from other authors on AUTHOR_ID’s post POST_ID

        try:
            author = Author.objects.get(pk=author_pk)
            post = author.post_set.get(pk=post_pk)
            likes = LikePost.objects.all().filter(object=post_pk)
            likesData = LikePostSerializer(likes, many=True).data
            return Response(likesData)
        except Post.DoesNotExist:
            return Response('Post doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
        except Author.DoesNotExist:
            return Response('Author doesn\'t exist', status=status.HTTP_404_NOT_FOUND)

    def post(self, request, author_pk, post_pk):
        # POST a like from the authenticated author on AUTHOR_ID’s post POST_ID
        if request.user.is_authenticated:

            author = Author.objects.get(pk=request.user.author.id)
            author_display_name = AuthorSerializer(
                author, many=False).data["displayName"]

            like_post = LikePost(
                id=f"{uuid.uuid4()}",
                object=f"{post_pk}",
                author=author,
                summary=f"{author_display_name} likes your post",
                url=f"{request.build_absolute_uri('/')}authors/{author_pk}/posts/{post_pk}"
            )

            like_post.save()
            like_post_serializer = LikePostSerializer(like_post)
            return Response(like_post_serializer.data)


class LikeCommentList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}/likes
    def get(self, request, author_pk, post_pk, comment_pk):
        try:
            author = Author.objects.get(pk=author_pk)
            post = author.post_set.get(pk=post_pk)
            comment = post.comment_set.get(pk=comment_pk)
            likes = LikeComment.objects.all().filter(comment_id=comment_pk)

            likesData = LikeCommentSerializer(likes, many=True).data
            return Response(likesData)

        except Author.DoesNotExist:
            return Response('Author doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response('Comment doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response('Post doesn\'t exist', status=status.HTTP_404_NOT_FOUND)

    def post(self, request, author_pk, post_pk, comment_pk):
        # POST a like from the authenticated author on AUTHOR_ID’s POST_ID's comment COMMENT_ID

        if request.user.is_authenticated:

            author = Author.objects.get(pk=request.user.author.id)
            author_display_name = AuthorSerializer(
                author, many=False).data["displayName"]

            like_comment = LikePost(
                id=f"{uuid.uuid4()}",
                object=f"{comment_pk}",
                author=author,
                summary=f"{author_display_name} likes your comment",
                url=f"{request.build_absolute_uri('/')}authors/{author_pk}/posts/{post_pk}/comments/{comment_pk}"
            )

            like_comment.save()
            like_comment_serializer = LikeCommentSerializer(like_comment)
            return Response(like_comment_serializer.data)


class AuthorLikesList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/liked
    def get(self, request, author_pk):
        try:
            author = Author.objects.get(pk=author_pk)

            post_likes = LikePost.objects.all().filter(author=author)
            post_likes_data = LikePostSerializer(post_likes, many=True).data

            comment_likes = LikeComment.objects.all().filter(author=author)
            comment_likes_data = LikeCommentSerializer(
                comment_likes, many=True).data

            finalData = {"type": "liked",
                         "items": post_likes_data + comment_likes_data}

            return Response(finalData)

        except Author.DoesNotExist:
            return Response('Author doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
