from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authors.models import Author
from authors.serializer import AuthorSerializer
from .models import Comment, Comments, Like, Post
from django.db.models import Q
from .serializer import PostSerializer, CreatePostSerializer, CommentSerializer, CommentsSerializer, LikeSerializer
from .models import Post, Comments, Comment
from inbox.models import Inbox
from authors.models import Author
import uuid


def get_object_from_url_or_404(model, url):
    '''
    Description:
    Attempts to return an item from the db using a url as the primary key

    Params:
    model: model
        Model object
    url: String
        Url to specific location

    Returns:
    Either returns the item if found otherwise if not found raise Http404
    '''
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
        '''
        Description:
        Gets the public post whose id is the primary key

        Params:
        request: request
        author_id: String
        postID: String

        Returns:
        Response containing the post
        '''
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def post(self, request, author_id, postID, format=None): # WIP (cannot handle an incomplete HTML form)
        '''
        Description:
        Updates the post whose id is pk

        Params:
        request: request
        author_id: String
        postID: String

        Returns:
        Response with an updated post and a status code of 200
        '''
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
        '''
        Description:
        Deletes the post whose id is pk

        Params:
        request: request
        author_id: String
        postID: String

        Returns:
        A response with status 200 and a message indicating post has been successfully deleted
        '''
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        post.delete()
        return Response('Post deleted successfully.', status=200)


class PostList(APIView):
    # URL ://service/authors/{AUTHOR_ID}/posts/
    serializer_class = CreatePostSerializer

    def get(self, request, author_id, format=None):
        '''
        Description:
        Gets recent posts from an author

        Params:
        request: request
        author_id: String

        Returns:
        Response containing the posts
        '''
        if paginated := 'page' in request.GET.keys():
            page = request.GET.get('page')
            page_size = request.GET.get('size') or 5
            try:
                page = int(page)
                page_size = int(page_size)
                assert page > 0
                assert page_size > 0
            except Exception:
                return Response("Bad query", status.HTTP_400_BAD_REQUEST)
        author = Author.objects.get(pk=author_id)
        posts = Post.objects.filter(author=author).order_by("-published")
        if paginated:
            page_index = (page-1)*page_size
            last_index = min(page_index+page_size, len(posts))
            posts = posts[page_index:last_index]
        data = PostSerializer(posts, many=True).data
        data = {'type':'posts', 'items':data}
        return Response(data)

    def post(self, request, author_id, format=None):
        '''
        Description:
        Creates a new post that contains a newly generated id

        Params:
        request: request
        author_id: String

        Returns:
        Response containing the new post with a status code of 200. If failed a message indicating failure will be sent instead with a status code of 204
        '''
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
                followers = Author.objects.filter(following__id__in=[author_id]).values_list('id', flat=True)
                # Add post to authors own inbox
                url = request.build_absolute_uri().split("posts")[0]
                inbox = get_object_from_url_or_404(Inbox, url)
                inbox.items.insert(0, PostSerializer(post).data)
                inbox.save()
                # Add post to the inbox of everyone who follows the author
                for follower in followers:
                        url = request.build_absolute_uri().split(author_id)[0]
                        url += follower + "/"
                        inbox = get_object_from_url_or_404(Inbox, url)
                        inbox.items.insert(0, PostSerializer(post).data)
                        inbox.save()
            return Response(PostSerializer(post).data, status=200)
        return Response('Post was unsuccessful. Please check the required information was filled out correctly again.', status=204)


class ImageDetail(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/image 
    def get(self, request, author_id, postID, format=None):
        '''
        Description:
        Gets a public post that is converted to binary as an image

        Params:
        request: request
        author_id: String
        postID: String

        Returns:
        Returns the image or 404 if image was not found
        '''
        author = Author.objects.get(pk=author_id)
        post = get_object_or_404(Post, pk=postID, author=author)
        if post.contentType not in [Post.JPEG, Post.PNG]:
            return Response(status=404)
        return Response(post.content)


class CommentDetail(APIView):
    def get(self, request, author_id, post_id, comment_id):
        '''
        Description:
        Gets a comment on a specific post

        Params:
        request: request
        author_id: String
        post_id: String
        comment_id: String

        Returns:
        Returns a response containing the comment
        '''
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
        '''
        Description:
        Gets the list of comments from a post

        Params:
        request: request
        author_id: String
        post_id: String

        Returns:
        Response containing the list of comments
        '''
        if paginated := 'page' in request.GET.keys():
            page = request.GET.get('page')
            page_size = request.GET.get('size') or 5
            try:
                page = int(page)
                page_size = int(page_size)
                assert page > 0
                assert page_size > 0
            except Exception:
                return Response("Bad query", status.HTTP_400_BAD_REQUEST)
        url = request.build_absolute_uri().split('?')[0] # trim off query params
        comments = get_object_from_url_or_404(Comments, url)
        comments.comments.set(comments.comments.order_by('published'))
        data = CommentsSerializer(comments).data
        if paginated:
            try:
                page_index = (page-1)*page_size
                last_index = min(page_index+page_size, len(data['comments']))
                data['comments'] = data['comments'][page_index:last_index]
                data['page'] = page
                data['size'] = page_size
            except Exception:
                return Response("Internal error", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data)

    def post(self, request, author_id, post_id, format=None):
        '''
        Description:
        Adds a comment to a post whose id is the primary key

        Params:
        request: request
        author_id: String
        post_id: String

        Returns:
        Response after comment has been added
        '''
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
        '''
        Description:
        Gets a list of likes from other authors on an authors specific post

        Params:
        request: request
        author_pk: String
        post_pk: String

        Returns:
        Returns response containing the likes on a post or HTTP_404_NOT_FOUND if either author or post does not exist
        '''
        uri = request.build_absolute_uri().split("/likes")[0]
        other_uri = uri[:-1] if uri[-1] == '/' else uri + '/'
        author = get_object_or_404(Author, pk=author_pk)
        post = get_object_or_404(Post, pk=post_pk, author=author)
        likes = Like.objects.all().filter(Q(object=uri) | Q(object=other_uri))
        likesData = LikeSerializer(likes, many=True).data
        return Response(likesData)
     

    def post(self, request, author_pk, post_pk):
        '''
        Description:
        Post a like from an authenticated author to a post

        Params:
        request: request
        author_pk: String
        post_pk: String

        Returns:
        Returns a response with the like added
        '''
        if request.user.is_authenticated:

            author = Author.objects.get(pk=request.user.author.id)
            author_display_name = AuthorSerializer(
                author, many=False).data["displayName"]
            
            object=f"{request.build_absolute_uri('/')}authors/{author_pk}/posts/{post_pk}"
            like = Like.objects.all().filter(object=object, author=author)

            #if like doesnt exist, create a new like object
            if len(like) == 0:
                like_post = Like(
                    context=f"TODO",
                    author=author,
                    summary=f"{author_display_name} likes your post",
                    object=f"{request.build_absolute_uri('/')}authors/{author_pk}/posts/{post_pk}"
                )

                like_post.save()
                like_post_serializer = LikeSerializer(like_post)
                return Response(like_post_serializer.data)
            else:
                return Response("You have liked this post already", status=status.HTTP_403_FORBIDDEN)

        else:
            return Response("You are not authenticated. Log in first", status=status.HTTP_401_UNAUTHORIZED)

class LikeCommentList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}/likes

    def get(self, request, author_pk, post_pk, comment_pk):
        '''
        Description:
        Gets a list of likes on an authors comment

        Params:
        request: request
        author_pk: String
        post_pk: String
        comment_pk: String

        Returns:
        Returns response containing the likes on a comment or HTTP_404_NOT_FOUND if author, post, or comment does not exist
        '''
        uri = request.build_absolute_uri().split("/likes")[0]
        other_uri = uri[:-1] if uri[-1] == '/' else uri + '/'
        author = get_object_or_404(Author, pk=author_pk)
        post = get_object_or_404(Post, pk=post_pk, author=author)
        comment = get_object_from_url_or_404(Comment, uri)
        likes = Like.objects.all().filter(Q(object=uri) | Q(object=other_uri))
        likesData = LikeSerializer(likes, many=True).data
        return Response(likesData)


    def post(self, request, author_pk, post_pk, comment_pk):
        '''
        Description:
        Post a like from the authenticated author to a comment

        Params:
        request: request
        author_pk: String
        post_pk: String
        comment_pk: String

        Returns:
        Returns a response with added like on comment
        '''

        if request.user.is_authenticated:

            author = Author.objects.get(pk=request.user.author.id)
            author_display_name = AuthorSerializer(
                author, many=False).data["displayName"]

            object=f"{request.build_absolute_uri('/')}authors/{author_pk}/posts/{post_pk}/comments/{comment_pk}"
            like = Like.objects.all().filter(object=object, author=author)
            
            #if like doesnt exist, create a new like object
            if len(like) == 0:
                like_comment = Like(
                    context = "TODO",
                    author=author,
                    summary=f"{author_display_name} likes your comment",
                    object=object
                )

                like_comment.save()
                like_comment_serializer = LikeSerializer(like_comment)
                return Response(like_comment_serializer.data)
            else:
                return Response("You have liked this comment already", status=status.HTTP_403_FORBIDDEN)


class AuthorLikesList(APIView):
    # URL: ://service/authors/{AUTHOR_ID}/liked
    def get(self, request, author_pk):
        '''
        Description:
        Gets a list of things the author has liked

        Params:
        request: request
        author_pk: String

        Returns:
        Returns response containing authors likes or if author does not exisst then status of 404
        '''
        try:
            author = Author.objects.get(pk=author_pk)

            likes = Like.objects.all().filter(author=author)
            likes_data = LikeSerializer(likes, many=True).data

            #TODO hide "friends only likes" from non-authenticated authors
            finalData = {"type": "liked",
                         "items": likes_data}
            return Response(finalData)

        except Author.DoesNotExist:
            return Response('Author doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
