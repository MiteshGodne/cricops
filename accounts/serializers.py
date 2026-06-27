from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'first_name', 'middle_name', 'last_name', 'password',
            'phone', 'role', 'avatar_url', 'is_email_verified',
            'is_phone_verified', 'date_joined'
        ]
        read_only_fields = [
            'user_id', 'is_email_verified', 'is_phone_verified', 
            'date_joined', 'email_verification_token'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'email': {'required': True, 'allow_blank': False}, 
            'first_name': {'required': True, 'allow_blank': False}, 
            'last_name': {'required': True, 'allow_blank': False}, 
            'phone': {
                'required' : True,
                'allow_blank' : False,
                'allow_null' : False,
                'validators': [
                    RegexValidator(
                        regex=r'^\d+$',
                        message='Phone field must contain numbers only.',
                        code='invalid_numeric'
                    )
                ]
            }
        }
    def validate_first_name(self, value):
        return value.upper()
    def validate_middle_name(self, value):
        return value.upper() if value is not None else value
    def validate_last_name(self, value):
        return value.upper()
        

    def create(self, validated_data):
        return User.objects.create_user(**validated_data) # >> Use your custom UserManager