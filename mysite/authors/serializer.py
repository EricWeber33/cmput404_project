from rest_framework import serializers
from .models import Author, FollowRequest

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    class Meta:
        model = Author
        fields = ('type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = ret['url']
        return ret

class FollowRequestSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FollowRequest
        fields = '__all__'
        