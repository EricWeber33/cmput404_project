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
        # if this is a remote author then change the id to represent the source rather than our internal representation
        if ret['host'] != "https://cmput404f22t17.herokuapp.com/" and ret['host'] != 'http://17.0.0.1:8000':
            host = ret['host']
            if host[-1] != '/':
                host = host + '/'
            if ret['id'][-1] == '/':
                ret['id'] = ret['id'][:-1]
            ret['id'] = host + 'authors/' +ret['id'].split('/')[-1]
        return ret


class FollowRequestSerializer(serializers.ModelSerializer):
    actor = AuthorSerializer()
    object = AuthorSerializer()
    class Meta:
        model = FollowRequest
        fields = '__all__'
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('id')
        ret['type'] = "Follow"
        return ret
        

class AuthorListSerializer(serializers.Serializer):
    type = serializers.CharField()
    items = AuthorSerializer(many=True)
