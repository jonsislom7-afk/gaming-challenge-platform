from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.accounts.models import EmailVerificationToken

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'role', 'total_points']
        read_only_fields = ['id', 'total_points']


class UserDetailSerializer(serializers.ModelSerializer):
    """Full user details"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'avatar',
            'bio', 'gender', 'birth_date', 'country', 'phone', 'role',
            'total_points', 'is_email_verified', 'is_banned', 'ban_until',
            'violation_count', 'created_at'
        ]
        read_only_fields = ['id', 'total_points', 'is_banned', 'ban_until', 'violation_count', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """User registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=['CHALLENGER', 'STREAMER'])
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'role']
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Email verification"""
    token = serializers.CharField(max_length=255)
    
    def validate_token(self, value):
        try:
            token_obj = EmailVerificationToken.objects.get(token=value)
            if not token_obj.is_valid():
                raise serializers.ValidationError("Token expired")
            return value
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token")
