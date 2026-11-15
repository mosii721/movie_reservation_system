from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id','user','phone_number','created_at']

    user = serializers.StringRelatedField(read_only=True)

    def create(self, validated_data):
        user_id = self.context['user_id']
        return Profile.objects.create(user_id=user_id,**validated_data)