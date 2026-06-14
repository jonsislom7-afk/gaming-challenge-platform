from rest_framework import views, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import EmailVerificationToken
from .serializers import (
    RegisterSerializer,
    UserDetailSerializer,
    UserBasicSerializer,
    EmailVerificationSerializer
)

User = get_user_model()


class RegisterView(views.APIView):
    """User registration - CHALLENGER yoki STREAMER"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Email verification token yaratish
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(hours=24)
            EmailVerificationToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # TODO: Email jo'natish
            # send_verification_email(user.email, token)
            
            return Response({
                'message': 'User registered successfully. Check your email to verify.',
                'user': UserBasicSerializer(user).data,
                'verification_token': token  # Development uchun, production'da olib tashlash
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(views.APIView):
    """Email verification"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token_obj = EmailVerificationToken.objects.get(
                    token=serializer.validated_data['token']
                )
                user = token_obj.user
                user.is_email_verified = True
                user.save()
                
                token_obj.delete()
                
                return Response({
                    'message': 'Email verified successfully',
                    'user': UserDetailSerializer(user).data
                })
            except EmailVerificationToken.DoesNotExist:
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """User login"""
    pass


class ProfileView(views.APIView):
    """Get/Update user profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserDetailSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckBanStatusView(views.APIView):
    """Check if user is banned"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if user.is_banned and user.ban_until:
            if timezone.now() > user.ban_until:
                # Ban vaqti tugadi
                user.is_banned = False
                user.ban_until = None
                user.violation_count = 0
                user.save()
            else:
                # Hali ban'da
                return Response({
                    'is_banned': True,
                    'ban_until': user.ban_until,
                    'message': f'You are banned until {user.ban_until}'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            'is_banned': False,
            'violation_count': user.violation_count
        })
