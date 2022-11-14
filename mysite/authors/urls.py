from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from django.views.generic.base import TemplateView # new
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('authors/', views.AuthorList.as_view()),
    re_path('^authors/(?P<pk>.+)/followers/$', views.FollowerList.as_view()),
    re_path('^authors/(?P<author_id>.+)/followers/(?P<foreign_author_id>.+)/$', views.FollowerDetail.as_view()),
    re_path('^authors/(?P<author_id>.*)/sendfollowrequest/$', views.MakeFollowRequest.as_view(), name='follow_request'),
    re_path('^authors/(?P<pk>.*)/', views.AuthorDetail.as_view(), name='author_detail'),

]

urlpatterns = format_suffix_patterns(urlpatterns)