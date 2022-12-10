from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path('^authors/(?P<pk>.+)/home/comment_submit/$', views.comment_submit),
    re_path('^authors/(?P<pk>.+)/explore/comment_submit/$', views.comment_submit),
    re_path('^authors/(?P<pk>.+)/home/post_submit/$', views.post_submit),
    re_path('^authors/(?P<pk>.+)/home/repost_submit/$', views.repost_submit),
    re_path('^authors/(?P<pk>.+)/home/send_follow/$', views.send_follow_request),
    re_path('^authors/(?P<pk>.+)/home/follow_respond/$', views.follow_request_respond),
    re_path('^authors/(?P<pk>.+)/home/edit_post/(?P<post_id>.+)/$', views.edit_post),
    re_path('^authors/(?P<pk>.+)/home/delete_post/(?P<post_id>.+)/$', views.delete_post),
    re_path('^authors/(?P<pk>.+)/home/$', views.homepage_view),
    re_path('^authors/(?P<pk>.+)/home/like_submit/$', views.like_submit),
    re_path('^authors/(?P<pk>.+)/explore/like_submit/$', views.like_submit),
    re_path('^authors/(?P<pk>.+)/explore/$', views.explore_posts),
    re_path('^authors/(?P<pk>.+)/githubactivity/$', views.github_activity),
    re_path('^authors/(?P<pk>.+)/profile/(?P<author_id>.+)/update_profile/$', views.update_profile),
    re_path('^authors/(?P<pk>.+)/profile/(?P<author_id>.+)/$', views.profile_page),
    re_path('^authors/(?P<pk>.+)/myfollowers/$', views.authors_followers),
]
urlpatterns = format_suffix_patterns(urlpatterns)
