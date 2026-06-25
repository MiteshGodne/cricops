from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'first_name', 'last_name', 'password',
            'phone', 'role', 'avatar_url', 'is_email_verified',
            'is_phone_verified', 'date_joined'
        ]
        read_only_fields = [
            'user_id', 'is_email_verified', 'is_phone_verified', 
            'date_joined', 'email_verification_token'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'email': {'required': True, 'allow_blank': False}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data) # >> Use your custom UserManager