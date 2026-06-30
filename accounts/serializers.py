from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import UserRole 
User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'first_name', 'middle_name', 'last_name', 'password', 'apply_for',
            'phone', 'role', 'avatar_url', 'is_email_verified',
            'is_phone_verified', 'date_joined'
        ]
        read_only_fields = [
            'user_id', 'role', 'is_email_verified', 'is_phone_verified', 'date_joined', 'email_verification_token'
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
    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id','email','first_name','middle_name','last_name','password','phone','apply_for','role','avatar_url','is_email_verified','date_joined']
        read_only_fields = ['user_id','role','is_email_verified','date_joined']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        role = self.initial_data.get('role')
        if role and role not in UserRole.values:
            raise serializers.ValidationError({"role": f"'{role}' is not a valid choice."})
        return attrs
    
    def create(self, validated_data):
        apply_for = validated_data.get('apply_for')
        role = UserRole.TEAMHEAD if apply_for == 'TEAMHEAD' else UserRole.PENDING
        validated_data['role'] = role
        return User.objects.create_user(**validated_data)