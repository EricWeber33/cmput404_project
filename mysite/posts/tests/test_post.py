import json
from unittest import skip
from django.test import RequestFactory, TestCase
from django.urls import resolve
from authors.models import Author
from inbox.models import Inbox
from ..views import CommentList, CommentDetail
from ..models import Post, Comment, Comments
from posts.serializer import CommentSerializer, PostSerializer, CommentsSerializer
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
# Create your tests here.

HOST = "http://testserver"
ID = "1"
ID2 = "2"
ID3 = "3"
URL = f'{HOST}/authors/{ID}'
URL2 = f'{HOST}/authors/{ID2}'
URL3 = f'{HOST}/authors/{ID3}'
POST_URL = f'{URL}/posts/{ID}/'
POST_URL = f'{URL2}/posts/{ID2}/'
COMMENTS_URL = f'{URL}/posts/{ID}/comments/'
COMMENTS_URL2 = f'{URL2}/posts/{ID2}/comments/'
COMMENT_ID = "commentid"
COMMENT_URL = f'{COMMENTS_URL}{COMMENT_ID}/'
COMMENT_ID2 = "commentid2"
COMMENT_URL2 = f'{COMMENTS_URL}{COMMENT_ID2}/'

def decode_bytes(byte):
    return json.loads(byte.decode("UTF-8"))
class PostsTest(APITestCase):
    
    def setUp(self):

        self.user = User.objects.create(
            username="test_user",
            email="test@gmail.com",
            password="testpassword"
        )

        self.user2 = User.objects.create(
            username="test_user2",
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
            profileImage='',
            user = self.user)
        self.author2 = Author.objects.create(
            id=ID2, 
            url=URL2,
            host=HOST,
            displayName="2",
            github='github',
            profileImage='',
            user = self.user2)
        self.author3 = Author.objects.create(
            id=ID3, 
            url=URL3,
            host=HOST,
            displayName="3",
            github='github',
            profileImage='',
            )
        self.comments = Comments.objects.create(
            post=POST_URL,
            id=COMMENTS_URL)
        self.comments2 = Comments.objects.create(
            post=POST_URL,
            id=COMMENTS_URL2)
        self.post = Post.objects.create(
            title='test post 1',
            id=ID,
            description='foo',
            contentType='text/plain',
            content='bar',
            author=self.author,
            count=0,
            comments=COMMENTS_URL,
            commentsSrc=self.comments,
            visibility='PUBLIC',
            unlisted=False
        )
        self.post2 = Post.objects.create(
            title='test post 2',
            id=ID2,
            description='foo',
            contentType='text/plain',
            content='bar',
            author=self.author2,
            count=0,
            comments=COMMENTS_URL2,
            commentsSrc=self.comments2,
            visibility='FRIENDS',
            unlisted=False
        )
        self.inbox = Inbox.objects.create(
            author=URL
        )
        self.inbox2 = Inbox.objects.create(
            author=URL2
        )
        self.inbox3 = Inbox.objects.create(
            author=URL3
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

        result = self.client.get(f'/authors/{ID}/inbox/')
        self.assertEqual(len(result.data['items']), 0)
        result = self.client.get(f'/authors/{ID2}/inbox/')
        self.assertEqual(len(result.data['items']), 0)

        ENDPOINT = f'/authors/{ID}/posts/'
        post_post_request = PostSerializer(self.post).data
        post_post_request['commentsSrc'] = CommentsSerializer(self.comments).data
        result = self.client.post(ENDPOINT, data=post_post_request, format='json')
        self.assertEqual(result.status_code, 200)

        result = self.client.get(f'/authors/{ID}/inbox/')
        self.assertEqual(len(result.data['items']), 1)
        result = self.client.get(f'/authors/{ID2}/inbox/')
        self.assertEqual(len(result.data['items']), 1)

    def test_post_pagination(self):
        ENDPOINT = f'{URL3}/posts/'
        for i in range(1,6):
            comment = Comments.objects.create(
                post=f'{ENDPOINT}3_{i}/',
                id=f'{ENDPOINT}3_{i}/comments',
            )
            Post.objects.create(
                title='i',
                id=f'3_{i}',
                description='foo',
                contentType='text/plain',
                content='bar',
                author=self.author3,
                count=0,
                comments=COMMENTS_URL,
                commentsSrc=comment,
                visibility='PUBLIC',
                unlisted=False
            )
        try:
            posts = PostSerializer(
                Post.objects.all().filter(author=self.author3).order_by('-published'),
                many=True).data
            res = self.client.get(ENDPOINT, QUERY_STRING="page=foo&size=bar")
            self.assertEqual(res.status_code, 400)
            res = self.client.get(ENDPOINT, QUERY_STRING="page=1&size=2")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data['items']), 2)
            self.assertEqual(res.data['items'], posts[:2])
            res = self.client.get(ENDPOINT, QUERY_STRING="page=2&size=2")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data['items']), 2)
            self.assertEqual(res.data['items'], posts[2:4])
            # test page size larger than remaining items
            res = self.client.get(ENDPOINT, QUERY_STRING="page=2&size=3")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data['items']), 2)
            self.assertEqual(res.data['items'], posts[3:])
        finally:
            posts = Post.objects.all().filter(author=self.author3)
            for post in posts:
                post.delete()
        

    def test_post_friends(self):

        # Check all inboxs empty
        result = self.client.get(f'/authors/{ID}/inbox/')
        self.assertEqual(len(result.data['items']), 0)
        result = self.client.get(f'/authors/{ID2}/inbox/')
        self.assertEqual(len(result.data['items']), 0)
        result = self.client.get(f'/authors/{ID3}/inbox/')
        self.assertEqual(len(result.data['items']), 0)

        #test: sending a valid follow request (author 1 attempts to follow author 2)
        response = self.client.post(f'{HOST}/authors/2/sendfollowrequest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Switch to user 2
        self.client.logout()
        self.client.force_login(self.user2)

        #test follow request is sent to the top of the object authors inbox
        response = self.client.get(f'{HOST}/authors/2/inbox/')
        inbox_items = decode_bytes(response.content).get('items')
        self.assertEqual(inbox_items[0].get("summary"), "1 wants to follow 2")

        #test accepting a follow request
        response = self.client.put(f'{HOST}/authors/2/followers/1/')
        self.assertEqual(decode_bytes(response.content), "Success. 1 follows you.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()
        self.client.force_login(self.user2)

        # Make post

        result = self.client.get(f'/authors/{ID}/inbox/')
        self.assertEqual(len(result.data['items']), 0)
        result = self.client.get(f'/authors/{ID2}/inbox/')
        self.assertEqual(len(result.data['items']), 1)              # Has 1 item in box due to follow request
        result = self.client.get(f'/authors/{ID3}/inbox/')
        self.assertEqual(len(result.data['items']), 0)

        ENDPOINT = f'/authors/{ID2}/posts/'
        post_post_request = PostSerializer(self.post2).data
        post_post_request['commentsSrc'] = CommentsSerializer(self.comments2).data
        result = self.client.post(ENDPOINT, data=post_post_request, format='json')
        self.assertEqual(result.status_code, 200)

        # Expect only inbox 1 and 2 to receive post due to 1 following 2 and 2 is the original poster
        result = self.client.get(f'/authors/{ID}/inbox/')
        self.assertEqual(len(result.data['items']), 1)
        result = self.client.get(f'/authors/{ID2}/inbox/')
        self.assertEqual(len(result.data['items']), 2)
        result = self.client.get(f'/authors/{ID3}/inbox/')
        self.assertEqual(len(result.data['items']), 0)


class CommentTest(APITestCase):

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
        self.comment = Comment.objects.create(
            author=Author.objects.get(pk=ID),
            id=COMMENT_URL,
            comment="test comment 1")
        self.comment2 = Comment.objects.create(
            author=Author.objects.get(pk=ID),
            id=COMMENT_URL2,
            comment = "test comment 2")
        comments = Comments.objects.create(
            post=POST_URL,
            id=COMMENTS_URL)
        comments.comments.add(self.comment)

    @skip('doesnt work')
    def test_post_comment(self):
        ENDPOINT = f'/authors/{ID}/posts/{ID}/comments/'
 
        comments_post_request = CommentSerializer(self.comment2).data
        result = self.client.post(ENDPOINT, data=comments_post_request, format='json')
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

    def test_pagination(self):
        post_url = f'{URL}/posts/2/'
        comments_url = f'{post_url}comments/'
        Post.objects.create(
            title  = 'test pagination',
            id = 2,
            source = '',
            description = 'foo',
            contentType = 'text/plain',
            content = 'bar',
            author = self.author,
            count = 0,
            unlisted = False)
        commentSrc = Comments.objects.create(
            post=post_url,
            id=comments_url
        )
        for i in range(1,6):
            commentSrc.comments.add(
                Comment.objects.create(
                    author=self.author,
                    id=f'{comments_url}{i}',
                    comment="test comment"
                )
            )
        comments = CommentsSerializer(commentSrc).data
        
        res = self.client.get(comments_url, QUERY_STRING='page=foo&size=bar')
        self.assertEqual(res.status_code, 400)
        res = self.client.get(comments_url, QUERY_STRING='page=1&size=2')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['page'], 1)
        self.assertEqual(res.data['size'], 2)
        self.assertEqual(comments['comments'][:2], res.data['comments'])
        res = self.client.get(comments_url, QUERY_STRING='page=2&size=2')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['page'], 2)
        self.assertEqual(res.data['size'], 2)
        self.assertEqual(comments['comments'][2:4], res.data['comments'])
        # test page size larger than remaining items
        res = self.client.get(comments_url, QUERY_STRING="page=2&size=3")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['comments']), 2)
        self.assertEqual(comments['comments'][3:], res.data['comments'])

    def test_get_comment(self):
        request = RequestFactory().get(f'/authors/{ID}/posts/{ID}/comments/{COMMENT_ID}/')
        view = CommentDetail()
        view.setup(request)
        result = view.get(request, ID, ID, COMMENT_ID)
        self.assertEqual(result.data['type'], 'comment')
        self.assertEqual(result.data['id'], COMMENT_URL)
        self.assertEqual(result.data['comment'], 'test comment 1')
    
