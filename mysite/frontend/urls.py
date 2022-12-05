from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path('^authors/(?P<pk>.+)/home/comment_submit/$', views.comment_submit),
    re_path('^authors/(?P<pk>.+)/home/post_submit/$', views.post_submit),
    re_path('^authors/(?P<pk>.+)/home/$', views.homepage_view),
    re_path('^authors/(?P<pk>.+)/home/like_post_submit/(?P<post_id>.+)/$', views.like_post_submit),
    re_path('^authors/(?P<pk>.+)/home/like_comment_submit/(?P<comments>.+)/(?P<comment_id>.+)/$', views.like_comment_submit),
    re_path('^authors/(?P<pk>.+)/explore/$', views.explore_posts),
]
urlpatterns = format_suffix_patterns(urlpatterns)