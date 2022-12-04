from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('posts/', views.PublicPostsList.as_view()),
    re_path('authors/(?P<author_pk>.*)/posts/(?P<post_pk>.*)/comments/(?P<comment_pk>.*)/likes/$',
             views.LikeCommentList.as_view()),
    re_path('authors/(?P<author_id>.*)/posts/(?P<post_id>.*)/comments/(?P<comment_id>.*)/$', views.CommentDetail.as_view()),
    re_path('authors/(?P<author_id>.*)/posts/(?P<post_id>.*)/comments/$', views.CommentList.as_view()),
    re_path('authors/(?P<author_pk>.*)/posts/(?P<post_pk>.*)/likes/$',
             views.LikePostList.as_view()),
    re_path('authors/(?P<author_id>.*)/posts/(?P<postID>.*)/image/$', views.ImageDetail.as_view()),
    re_path('authors/(?P<author_id>.*)/posts/(?P<postID>.*)/$', views.PostDetail.as_view()),
    re_path('authors/(?P<author_id>.*)/posts/$', views.PostList.as_view()),
    re_path('authors/(?P<author_pk>.*)/liked/$',views.AuthorLikesList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)