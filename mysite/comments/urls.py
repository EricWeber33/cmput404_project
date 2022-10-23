from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path('author/(?P<pk>.+)/post/(?P<pk>.+)/comments', views.CommentList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)