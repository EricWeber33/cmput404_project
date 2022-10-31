from rest_framework import serializers
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    class Meta:
        model = Author
        fields = ('type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = ret['url']
        return ret