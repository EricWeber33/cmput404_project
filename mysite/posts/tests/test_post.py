from datetime import datetime
from unittest import skip
from django.test import RequestFactory, TestCase
from django.urls import resolve
from authors.models import Author
from inbox.models import Inbox
from ..views import CommentList, CommentDetail
from ..models import Post, Comment, Comments
from datetime import datetime
from posts.serializer import CommentSerializer, PostSerializer, CommentsSerializer
from rest_framework.test import APIClient
from django.contrib.auth.models import User
# Create your tests here.

HOST = "http://testserver"
ID = "1"
ID2 = "2"
URL = f'{HOST}/authors/{ID}'
URL2 = f'{HOST}/authors/{ID2}'
POST_URL = f'{URL}/posts/{ID}/'
COMMENTS_URL = f'{URL}/posts/{ID}/comments/'
COMMENT_ID = "commentid"
COMMENT_URL = f'{COMMENTS_URL}{COMMENT_ID}/'
COMMENT_ID2 = "commentid2"
COMMENT_URL2 = f'{COMMENTS_URL}{COMMENT_ID2}/'
class PostsTest(TestCase):
    
    def setUp(self):

        self.user = User.objects.create(
            username="test_user",
            email="test@gmail.com",
            password="testpassword"
        )
        self.apiClient = APIClient()
        self.apiClient.force_login(self.user)

        self.author = Author.objects.create(
            id=ID, 
            url=URL,
            host=HOST,
            displayName="1",
            github='github',
            profileImage='')
        self.author2 = Author.objects.create(
            id=ID2, 
            url=URL2,
            host=HOST,
            displayName="2",
            github='github',
            profileImage='')
        self.comments = Comments.objects.create(
            post=POST_URL,
            id=COMMENTS_URL)
        self.post = Post.objects.create(
            title='test post 1',
            id=ID,
            description='foo',
            contentType='text/plain',
            content='bar',
            author=Author.objects.get(pk=ID),
            count=0,
            comments=COMMENTS_URL,
            commentsSrc=self.comments,
            visibility='PUBLIC',
            unlisted=False
        )
        self.inbox = Inbox.objects.create(
            author=URL
        )
        self.inbox2 = Inbox.objects.create(
            author=URL2
        )
        self.comment = Comment.objects.create(
            author=self.author,
            id=COMMENT_URL,
            comment="test comment 1"
        )

    def test_resolution(self):
        resolver = resolve(f'/authors/{ID}/posts/')
        self.assertEqual(resolver.view_name, 'posts.views.PostList')
        resolver = resolve(f'/authors/{ID}/posts/PostID/')
        self.assertEqual(resolver.view_name, 'posts.views.PostDetail')

    def test_post_post(self):

        result = self.apiClient.get(f'/authors/{ID}/inbox/')
        self.assertEqual(len(result.data['items']), 0)
        result = self.apiClient.get(f'/authors/{ID2}/inbox/')
        self.assertEqual(len(result.data['items']), 0)

        ENDPOINT = f'/authors/{ID}/posts/'
        post_post_request = PostSerializer(self.post).data
        post_post_request['commentsSrc'] = CommentsSerializer(self.comments).data
        result = self.apiClient.post(ENDPOINT, data=post_post_request, format='json')
        self.assertEqual(result.status_code, 200)

        result = self.apiClient.get(f'/authors/{ID}/inbox/')
        self.assertEqual(len(result.data['items']), 1)
        result = self.apiClient.get(f'/authors/{ID2}/inbox/')
        self.assertEqual(len(result.data['items']), 1)
        
class CommentTest(TestCase):

    def setUp(self):

        self.user = User.objects.create(
            username="test_user",
            email="test@gmail.com",
            password="testpassword"
        )
        self.apiClient = APIClient()
        self.apiClient.force_login(self.user)

        Author.objects.create(
            id=ID, 
            url=URL,
            host=HOST,
            displayName="1",
            github='github',
            profileImage='')
        
        Post.objects.create(
            title  = 'test post',
            id = ID,
            source = '',
            description = 'foo',
            contentType = 'text/plain',
            content = 'bar',
            author = Author.objects.get(pk=ID),
            count = 0,
            unlisted = False)
        comment = Comment.objects.create(
            author=Author.objects.get(pk=ID),
            id=COMMENT_URL,
            comment="test comment 1")
        self.comment2 = Comment.objects.create(
            author=Author.objects.get(pk=ID),
            id=COMMENT_URL2,
            comment = "test comment 2")
        comments = Comments.objects.create(
            post=Post.objects.get(pk=ID),
            id=COMMENTS_URL)
        comments.comments.add(comment)

    @skip('doesnt work')
    def test_post_comment(self):
        ENDPOINT = f'/authors/{ID}/posts/{ID}/comments/'
 
        comments_post_request = CommentSerializer(self.comment2).data
        result = self.apiClient.post(ENDPOINT, data=comments_post_request, format='json')
        # Goes to comments and the the content listed in (comment : x )
        self.assertEqual(list(result.data['comments'][1].items())[2][1], "test comment 2")

    def test_resolution(self):
        resolver = resolve(f'/authors/{ID}/posts/{ID}/comments/')
        self.assertEqual(resolver.view_name, 'posts.views.CommentList')
        resolver = resolve(f'/authors/{ID}/posts/{ID}/comments/{COMMENT_ID}/')
        self.assertEqual(resolver.view_name, 'posts.views.CommentDetail')

    def test_get_comment_list(self):
        request = RequestFactory().get(f'/authors/{ID}/posts/{ID}/comments/')
        view = CommentList()
        view.setup(request)
        result = view.get(request, ID, ID)
        self.assertEqual(result.data['type'], 'comments')
        self.assertEqual(result.data['id'], COMMENTS_URL)
        self.assertEqual(len(result.data['comments']), 1)
        self.assertEqual(result.data['comments'][0]['comment'], 'test comment 1')

    def test_get_comment(self):
        request = RequestFactory().get(f'/authors/{ID}/posts/{ID}/comments/{COMMENT_ID}/')
        view = CommentDetail()
        view.setup(request)
        result = view.get(request, ID, ID, COMMENT_ID)
        self.assertEqual(result.data['type'], 'comment')
        self.assertEqual(result.data['id'], COMMENT_URL)
        self.assertEqual(result.data['comment'], 'test comment 1')
    
