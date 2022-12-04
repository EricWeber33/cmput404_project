from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path('authors/(?P<pk>.*)/inbox/$', views.InboxView.as_view()),
    re_path('authors/(?P<pk>.*)/inbox$', views.InboxView.as_view())
]

