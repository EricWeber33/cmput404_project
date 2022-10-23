from cgitb import text
from datetime import datetime
from unittest import skip
from xmlrpc.client import NOT_WELLFORMED_ERROR
from django.test import RequestFactory, TestCase
from django.urls import resolve
from authors.models import Author
from .models import Post
from datetime import datetime
# Create your tests here.

HOST = "http://testserver"
ID = "postTestBoy"
URL = f'{HOST}/authors/{ID}'

class PostsTest(TestCase):
    
    def setUp(self):
        Author.objects.create(
            id=ID, 
            url=URL,
            host=HOST,
            displayName="1",
            github='github',
            profileImage='',
        )
        Post.objects.create(
            title = "Test",
            id="PostID",
            description="This is a test.",
            contentType="text",
            content="dfnsofndsojfndjfndjsfds",
            author=Author.objects.get(pk=ID),
            count=0,
            published=datetime.now(),
            visibility="PUBLIC",
            unlisted = False,
        )


    def test_resolution(self):
        resolver = resolve('/authors/postTestBoy/posts/PostID')
        self.assertEqual(resolver.view_name, 'posts.views.PostDetail')