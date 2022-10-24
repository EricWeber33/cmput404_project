from rest_framework import serializers
from .models import LikePost, LikeComment

class LikeCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikeComment
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['object'] = ret['url']
        ret.pop('url')
        return ret

class LikePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikePost
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['object'] = ret['url']
        ret.pop('url')
        return ret