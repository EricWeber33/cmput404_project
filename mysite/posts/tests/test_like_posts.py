from datetime import datetime

import urllib
from authors.models import Author
from ..models import LikePost, Post

import json
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

# Create your tests here.

HOST = "http://testserver"
ID = "postTest"
URL = f'{HOST}/authors/{ID}'


def get_dict(byte):
    return json.loads(byte.decode("UTF-8"))


class LikePostsTest(APITestCase):
    def setUp(self):
        self.apiClient = APIClient()

        Author.objects.create(
            id="1", 
            url=URL,
            host=HOST,
            displayName="test user 1",
            github='github',
            profileImage='',
        )

        Author.objects.create(
            id="2", 
            url=URL,
            host=HOST,
            displayName="test user 2",
            github='github',
            profileImage='',
        )

        Post.objects.create(
            title = "Test",
            id="PostID",
            description="This is a test.",
            contentType="text",
            content="dfnsofndsojfndjfndjsfds",
            author=Author.objects.get(pk="1"),
            count=0,
            published=datetime.now(),
            visibility="PUBLIC",
            unlisted = False,
        )

        LikePost.objects.create(
            id = "1",
            object = "PostID",
            author = Author.objects.get(pk="2"),
            summary = "test user 2 likes your post",
            url = f'{HOST}/authors/1/posts/PostID',
        )

    def test_get_author_likes_list(self):
        response = self.apiClient.get(f'{HOST}/authors/2/liked')

        dict = get_dict(response.content).get('items')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(dict))
        self.assertEqual("test user 2 likes your post", dict[0].get('summary'))
    
    def test_get_post_likes_list(self):
        response = self.apiClient.get(f'{HOST}/authors/1/posts/PostID/likes', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        dict = response.data[0]
        self.assertEqual("test user 2 likes your post", dict.get('summary'))
        self.assertEqual(f'{HOST}/authors/1/posts/PostID', dict.get('object'))


