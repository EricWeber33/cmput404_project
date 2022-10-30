from tkinter import END
from django.urls import resolve
from authors.models import Author
from posts.serializer import CommentSerializer, CommentsSerializer, PostSerializer
from rest_framework.test import APITestCase
from posts.models import Comment, Comments, Post
from django.contrib.auth.models import User
from .models import Inbox
import json
# Create your tests here.

HOST = "http://testserver"
ID = "1"
ID2 = "2"
URL = f'{HOST}/authors/{ID}'
POST_URL = f'{URL}/posts/{ID}/'
COMMENTS_URL = f'{POST_URL}comments/'
COMMENT_URL = f'{COMMENTS_URL}{ID}'

class InboxTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            email="test@gmail.com",
            password="testpassword"
        )
        self.client.force_login(self.user)
        self.author = Author.objects.create(
            id=ID, 
            url=URL,
            host=HOST,
            displayName="1",
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
            unlisted=False
        )
        self.inbox = Inbox.objects.create(
            author=URL
        )
        self.comment = Comment.objects.create(
            author=self.author,
            id=COMMENT_URL,
            comment="test comment 1"
        )

    def test_resolution(self):
        resolver = resolve('/authors/testinboxid/inbox/')
        self.assertEqual(resolver.view_name, 'inbox.views.InboxView')
    
    def test_get_inbox(self):
        result = self.client.get(f'/authors/{ID}/inbox/')
        self.assertEqual(result.data['type'], "inbox")
        self.assertEqual(result.data['author'], URL)
        self.assertIn('items', result.data.keys())


    def test_post_inbox(self):
        
        ENDPOINT = f'/authors/{ID}/inbox/'

        # test unknown type
        result = self.client.post(ENDPOINT, {})
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, "Unknown type")
        # test malformed post
        result = self.client.post(ENDPOINT, {"type":"post","foo":"bar"})
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, "Invalid post object")
        # test malformed comment
        result = self.client.post(ENDPOINT,{"type":"comment","foo":"bar"})
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, "Invalid comment object")
        # test malformed follow request

        # test malformed like 

        # test posting of post object
        post_post_request = PostSerializer(self.post).data
        post_post_request['commentsSrc'] = CommentsSerializer(self.comments).data
        result = self.client.post(ENDPOINT, data=post_post_request, format='json')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.data['items']), 1)
        self.assertEqual(result.data['items'][0], post_post_request)
        # test posting of comment
        post_comment_request = CommentSerializer(self.comment).data
        result = self.client.post(ENDPOINT, data=post_comment_request, format='json')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data['items'][0], post_comment_request)
        # test posting of follow request

        # test posting of like

        # test ordering of inbox
        # expected inbox.items is [like, follow, comment, post]
        self.assertEqual(result.data['items'], [post_comment_request, post_post_request])
        #clear the inbox for other tests
        self.inbox.items.clear()
        self.inbox.save()


    def test_delete_inbox(self):
        stub_post = json.dumps({"type":"post","content":"test content"})
        stub_post2 = json.dumps({"type":"post","content":"test content 2"})
        self.inbox.items.insert(0, stub_post)
        self.inbox.items.insert(0, stub_post2)
        self.inbox.save()
        result = self.client.get(f'/authors/{ID}/inbox/')
        self.assertEqual(result.data['type'], "inbox")
        self.assertEqual(result.data['author'], URL)
        self.assertEqual(result.data['items'], [stub_post2, stub_post])
        result = self.client.delete(f'/authors/{ID}/inbox/')
        self.assertEqual(result.data['type'], "inbox")
        self.assertEqual(result.data['author'], URL)
        self.assertEqual(result.data['items'], [])