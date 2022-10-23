from django.test import RequestFactory, TestCase
from django.urls import resolve
from authors.models import Author
from posts.models import Post, Comment
from .models import Comments
from .views import CommentList
# Create your tests here.

HOST = "http://127.0.0.1:8080"
ID = "commentstestid"
URL = f'{HOST}'/authors/'{ID}'

class CommentTest(TestCase):

    def setUp(self):
        Author.objects.create(
            id=ID, 
            url=URL,
            host=HOST,
            displayName="1",
            github='github',
            profileImage='')

        Post.objects.create(
            title  = '',
            id = ID,
            source = '',
            description = '',
            contentType = PLAIN,
            conteont = '',
            author = URL,
            categories = '',
            count = 1,
            comments = '',
            published = '',
            visibility = PUBLIC,
            unlisted = False)

# Create your tests here.
