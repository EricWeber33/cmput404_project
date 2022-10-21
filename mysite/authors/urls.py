from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('authors/', views.AuthorList.as_view()),
    re_path('^authors/(?P<pk>.+)/followers/$', views.FollowerList.as_view()),
    re_path('^authors/(?P<pk>.+)/followers/(?P<foreign>.+)/$', views.FollowerList.as_view()),
    re_path('^authors/(?P<pk>.+)/$', views.AuthorDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)