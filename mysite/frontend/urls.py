from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path('^authors/(?P<pk>.+)/home/comment_submit/$', views.comment_submit),
    re_path('^authors/(?P<pk>.+)/home/post_submit/$', views.post_submit),
    re_path('^authors/(?P<pk>.+)/home/repost_submit/(?P<post_id>.+)/$', views.repost_submit),
    re_path('^authors/(?P<pk>.+)/home/$', views.homepage_view),
]
urlpatterns = format_suffix_patterns(urlpatterns)