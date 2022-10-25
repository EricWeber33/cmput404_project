from datetime import datetime
from unittest import skip
from django.test import RequestFactory, TestCase
from django.urls import resolve
from authors.models import Author
from .views import CommentList, CommentDetail
from .models import Post, Comment, Comments
from datetime import datetime
# Create your tests here.

HOST = "http://testserver"
ID = "1"
URL = f'{HOST}/authors/{ID}'
COMMENTS_URL = f'{URL}/posts/{ID}/comments/'
COMMENT_ID = "commentid"
COMMENT_URL = f'{COMMENTS_URL}{COMMENT_ID}/'
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
        resolver = resolve(f'/authors/{ID}/posts/')
        self.assertEqual(resolver.view_name, 'posts.views.PostList')
        resolver = resolve(f'/authors/{ID}/posts/PostID/')
        self.assertEqual(resolver.view_name, 'posts.views.PostDetail')
        
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
        comments = Comments.objects.create(
            post=Post.objects.get(pk=ID),
            id=COMMENTS_URL)
        comments.comments.add(comment)

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
    
