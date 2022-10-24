from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('authors/<str:author_pk>/posts/<str:post_pk>/likes/$',
             views.LikePostList.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)