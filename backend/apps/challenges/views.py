from rest_framework import views, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta

from .models import Challenge, DailyChallenge, UserChallenge, ChallengerViolation, GameCategory
from .serializers import (
    ChallengeSerializer,
    CreateChallengeSerializer,
    DailyChallengeSerializer,
    UserChallengeSerializer,
    SubmitChallengeSerializer,
    ChallengerViolationSerializer,
    GameCategorySerializer
)
from apps.payments.models import UserSubscription


class GameCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Game categories - dunyodagi oyinlar"""
    queryset = GameCategory.objects.filter(is_active=True)
    serializer_class = GameCategorySerializer
    permission_classes = [IsAuthenticated]


class DailyChallengeView(views.APIView):
    """Kunlik challenges - har kuni boshqa"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Ban tekshirish
        if user.is_banned and user.ban_until and timezone.now() < user.ban_until:
            return Response(
                {'error': f'You are banned until {user.ban_until}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = date.today()
        daily_challenge = DailyChallenge.objects.filter(date=today).first()
        
        if not daily_challenge:
            # Yangi daily challenge yaratish
            approved_challenges = Challenge.objects.filter(status='APPROVED')
            if approved_challenges.exists():
                import random
                challenge = random.choice(list(approved_challenges))
                daily_challenge = DailyChallenge.objects.create(
                    challenge=challenge,
                    date=today
                )
        
        if daily_challenge:
            # Premium-only challenges
            challenge = daily_challenge.challenge
            user_subscription = user.subscription if hasattr(user, 'subscription') else None
            
            if challenge.is_premium_only:
                if not (user_subscription and user_subscription.is_active and user_subscription.plan):
                    return Response(
                        {'error': 'This challenge requires premium subscription'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer = DailyChallengeSerializer(daily_challenge)
            return Response(serializer.data)
        
        return Response(
            {'error': 'No challenges available'},
            status=status.HTTP_404_NOT_FOUND
        )


class CreateChallengeView(views.APIView):
    """CHALLENGER - new challenge yaratish"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Faqat CHALLENGER qila oladi
        if user.role != 'CHALLENGER':
            return Response(
                {'error': 'Only challengers can create challenges'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ban tekshirish
        if user.is_banned and user.ban_until and timezone.now() < user.ban_until:
            return Response(
                {'error': f'You are banned until {user.ban_until}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Kunlik limit tekshirish (tekin versiya - 3 ta)
        today = date.today()
        daily_count = Challenge.objects.filter(
            challenger=user,
            created_at__date=today
        ).count()
        
        # Subscription tekshirish
        user_subscription = user.subscription if hasattr(user, 'subscription') else None
        
        if user_subscription and user_subscription.is_active and user_subscription.plan:
            # Obuna olgan - cheksiz
            pass
        else:
            # Tekin - 3 ta
            if daily_count >= 3:
                return Response(
                    {'error': 'Daily limit reached (3). Subscribe for unlimited.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = CreateChallengeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChallengeListView(views.APIView):
    """STREAMER - o'z challenges'i"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'STREAMER':
            return Response(
                {'error': 'Only streamers can view challenges'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        challenges = UserChallenge.objects.filter(user=user)
        serializer = UserChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


class SubmitChallengeView(views.APIView):
    """STREAMER - challenge yakunlash"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, challenge_id):
        user = request.user
        
        if user.role != 'STREAMER':
            return Response(
                {'error': 'Only streamers can submit challenges'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ban tekshirish
        if user.is_banned and user.ban_until and timezone.now() < user.ban_until:
            return Response(
                {'error': f'You are banned until {user.ban_until}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            challenge = Challenge.objects.get(pk=challenge_id, status='APPROVED')
        except Challenge.DoesNotExist:
            return Response(
                {'error': 'Challenge not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_challenge, created = UserChallenge.objects.get_or_create(
            user=user,
            challenge=challenge
        )
        
        serializer = SubmitChallengeSerializer(
            user_challenge,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            user_challenge.status = 'SUBMITTED'
            user_challenge.submitted_at = timezone.now()
            user_challenge.save()
            return Response(UserChallengeSerializer(user_challenge).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteChallengeView(views.APIView):
    """ADMIN - challenge'ni tasdig'i va points berish"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_challenge_id):
        user = request.user
        
        if user.role != 'ADMIN':
            return Response(
                {'error': 'Only admins can approve challenges'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user_challenge = UserChallenge.objects.get(pk=user_challenge_id)
        except UserChallenge.DoesNotExist:
            return Response(
                {'error': 'Challenge not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_approved = request.data.get('is_approved', False)
        
        if is_approved:
            user_challenge.status = 'COMPLETED'
            user_challenge.completed_at = timezone.now()
            user_challenge.points_earned = user_challenge.challenge.reward_points
            
            # User points yangilash
            user_challenge.user.total_points += user_challenge.points_earned
            user_challenge.user.save()
        else:
            user_challenge.status = 'FAILED'
        
        user_challenge.save()
        return Response(UserChallengeSerializer(user_challenge).data)


class ReportChallengerView(views.APIView):
    """Challenge'ni report qilish (sokinish - violation)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, challenge_id):
        try:
            challenge = Challenge.objects.get(pk=challenge_id)
        except Challenge.DoesNotExist:
            return Response(
                {'error': 'Challenge not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ChallengerViolationSerializer(data=request.data)
        if serializer.is_valid():
            violation = serializer.save(
                challenger=challenge.challenger,
                challenge=challenge
            )
            return Response(
                ChallengerViolationSerializer(violation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
