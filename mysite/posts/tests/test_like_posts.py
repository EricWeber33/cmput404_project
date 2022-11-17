from datetime import datetime
from django.urls import resolve
from authors.models import Author
from ..models import Like, Post, Comment, Comments
from ..serializer import LikeSerializer
from django.contrib.auth.models import User

import json
from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.

HOST = "http://testserver"
ID = "1"
ID2 = "2"
URL = f'{HOST}/authors/{ID}'
URL2 = f'{HOST}/authors/{ID2}'
POST_URL = f'{URL}/posts/PostID'
COMMENTS_URL = f'{POST_URL}/comments'
COMMENT_URL = f'{COMMENTS_URL}/1'


def get_dict(byte):
    return json.loads(byte.decode("UTF-8"))


class LikePostsTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            email="test@gmail.com",
            password="testpassword"
        )
        self.client.force_login(self.user)
        self.author1 = Author.objects.create(
            id=ID, 
            url=URL,
            host=HOST,
            displayName="test user 1",
            github='github',
            profileImage='',
            user=self.user
        )

        self.author2 = Author.objects.create(
            id=ID2, 
            url=URL2,
            host=HOST,
            displayName="test user 2",
            github='github',
            profileImage='',
        )
        self.comments = Comments.objects.create(
            post=POST_URL,
            id=COMMENTS_URL
        )
        self.post = Post.objects.create(
            title = "Test",
            id="PostID",
            description="This is a test.",
            contentType="text",
            content="foobar",
            author=self.author1,
            count=0,
            published=datetime.now(),
            visibility="PUBLIC",
            unlisted = False,
        )
        self.comment = Comment.objects.create(
            author=self.author2,
            id=COMMENT_URL,
            comment="test comment"
        )
        self.like = Like.objects.create(
            context="test",
            author=self.author2,
            summary="test user 2 likes your post",
            object=POST_URL,
        )
        self.comment_like = Like.objects.create(
            context="test comment like",
            author=self.author1,
            summary="test user 1 likes your comment",
            object=COMMENT_URL,
        )

    def test_resolution(self):
        resolver = resolve('/authors/1/posts/1/likes/')
        self.assertEqual(resolver.view_name, 'posts.views.LikePostList')
        resolver = resolve('/authors/1/posts/1/comments/1/likes/')
        self.assertEqual(resolver.view_name, 'posts.views.LikeCommentList')

    def test_get_author_likes_list(self):
        response = self.client.get(f'{HOST}/authors/2/liked/')
        res = get_dict(response.content).get('items')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res))
        self.assertEqual("test user 2 likes your post", res[0].get('summary'))
    
    def test_get_post_likes_list(self):
        response = self.client.get(f'{POST_URL}/likes/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        res = response.data[0]
        self.assertEqual("test user 2 likes your post", res.get('summary'))
        self.assertEqual(POST_URL, res.get('object'))

    def test_get_comment_likes_list(self):
        response = self.client.get(f'{COMMENT_URL}/likes/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        res = response.data[0]
        self.assertEqual("test user 1 likes your comment", res.get('summary'))
        self.assertEqual(COMMENT_URL, res.get('object'))


