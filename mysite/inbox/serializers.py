from rest_framework import serializers

from posts.models import Post
from .models import Inbox
from posts.serializer import PostSerializer

class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = ('type', 'author', 'items')