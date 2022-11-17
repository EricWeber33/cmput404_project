
import json
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from authors.models import Author, FollowRequest
from django.contrib.auth.models import User
from inbox.models import Inbox
from django.urls import resolve
from .serializer import AuthorSerializer
# Create your tests here.

HOST = "http://testserver"

def decode_bytes(byte):
    return json.loads(byte.decode("UTF-8"))
class FollowTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(
            username="test_user1",
            email="test@gmail.com",
            password="testpassword"
        )

        self.user2 = User.objects.create(
            username="test_user2",
            email="test@gmail.com",
            password="testpassword"
        )
        self.apiClient = APIClient()
        self.apiClient.force_login(self.user1)

        Author.objects.create(
            id="1", 
            url=f'{HOST}/authors/1',
            host=HOST,
            displayName="test user 1",
            github='github',
            profileImage='',
            user = self.user1
        )

        Author.objects.create(
            id="2", 
            url=f'{HOST}/authors/2',
            host=HOST,
            displayName="test user 2",
            github='github',
            profileImage='',
            user = self.user2
        )

        Author.objects.create(
            id="3", 
            url=f'{HOST}/authors/3',
            host=HOST,
            displayName="test user 3",
            github='github',
            profileImage='',
        )

        Inbox.objects.create(
            author=f'{HOST}/authors/2'
        )

    def test_followers(self):
        
        #test: cannot send a follow request to yourself
        response = self.apiClient.post(f'{HOST}/authors/1/sendfollowrequest/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #test: sending a valid follow request
        response = self.apiClient.post(f'{HOST}/authors/2/sendfollowrequest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dict = response.data
        self.assertEqual("test user 1 wants to follow test user 2", dict.get('summary'))
        self.assertEqual('2', dict.get('object'))
        
        #test authors can only add their own followers/accept their own follow requests
        response = self.apiClient.put(f'{HOST}/authors/2/followers/1/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.apiClient.logout()
        self.apiClient.force_login(self.user2)

        #test follow request is sent to the top of the object authors inbox
        response = self.apiClient.get(f'{HOST}/authors/2/inbox/')
        inbox_items = decode_bytes(response.content).get('items')
        self.assertEqual(inbox_items[0].get("summary"), "test user 1 wants to follow test user 2")

        #test accepting a follow request
        response = self.apiClient.put(f'{HOST}/authors/2/followers/1/')
        self.assertEqual(decode_bytes(response.content), "Success. test user 1 follows you.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #test get follower list
        response = self.apiClient.get(f'{HOST}/authors/2/followers/')

        follower_list = decode_bytes(response.content).get('items')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(follower_list))
        self.assertEqual("http://testserver/authors/1", follower_list[0].get("id"))
        self.assertEqual("test user 1", follower_list[0].get("displayName"))

        #test get is_follower?
        response = self.apiClient.get(f'{HOST}/authors/2/followers/3/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decode_bytes(response.content), "test user 3 does not follow test user 2")

        response = self.apiClient.get(f'{HOST}/authors/2/followers/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decode_bytes(response.content), "test user 1 follows test user 2")

        #test delete a follower
        response = self.apiClient.delete(f'{HOST}/authors/2/followers/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decode_bytes(response.content), "test user 1 unfollowed test user 2 successfully")

        response = self.apiClient.get(f'{HOST}/authors/2/followers/')
        follower_list = decode_bytes(response.content).get('items')
        self.assertEqual(0, len(follower_list))




class AuthorsTest(APITestCase):

    ENDPOINT = f'{HOST}/authors/'

    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            email="test@email.com",
            password="testpassword"
        )
        self.client.force_login(self.user)
        self.authors = [
            Author.objects.create(
                id=str(i),
                url=f'{HOST}/authors/{i}',
                host=HOST,
                displayName=f'Author{i}',
                github='github',
                profileImage='',
            ) for i in range(1, 6)
        ]
        self.author = self.authors[0]

    def test_resolution(self):
        resolver = resolve('/authors/')
        self.assertEqual(resolver.view_name, 'authors.views.AuthorList')
        resolver = resolve('/authors/1/')
        self.assertEqual(resolver.view_name, 'author_detail')

    def test_get_author(self):
        author1_url = f'{self.ENDPOINT}1' 
        res = self.client.get('/authors/1/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['type'], 'author')
        self.assertEqual(res.data['id'], res.data['url'])
        self.assertEqual(res.data['url'], author1_url)
        self.assertEqual(res.data['displayName'], 'Author1')

    def test_get_authors(self):
        res = self.client.get('/authors/')
        authors = Author.objects.all().order_by('-id')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['type'], 'authors')
        self.assertEqual(len(res.data['items']), 5)
        self.assertEqual(res.data['items'], AuthorSerializer(authors, many=True).data)

    def test_authors_pagination(self):
        authors = AuthorSerializer(Author.objects.all().order_by('-id'), many=True).data
        res = self.client.get('/authors/', QUERY_STRING="page=foo&size=bar")
        self.assertEqual(res.status_code, 400)
        res = self.client.get('/authors/', QUERY_STRING="page=1&size=2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['items']), 2)
        self.assertEqual(res.data['items'], authors[:2])
        res = self.client.get('/authors/', QUERY_STRING="page=2&size=2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['items']), 2)
        self.assertEqual(res.data['items'], authors[2:4])
        # test page size larger than remaining items
        res = self.client.get('/authors/', QUERY_STRING="page=2&size=3")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['items']), 2)
        self.assertEqual(res.data['items'], authors[3:])

