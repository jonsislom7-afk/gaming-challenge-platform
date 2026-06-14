from rest_framework import views, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Leaderboard
from .serializers import LeaderboardSerializer


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Leaderboard"""
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['period']
    ordering = ['rank']


class GlobalLeaderboardView(views.APIView):
    """Global leaderboard - top 100"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        leaderboard = Leaderboard.objects.filter(
            period='ALL_TIME'
        ).order_by('rank')[:100]
        serializer = LeaderboardSerializer(leaderboard, many=True)
        return Response(serializer.data)


class MonthlyLeaderboardView(views.APIView):
    """Monthly leaderboard - top 100"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        leaderboard = Leaderboard.objects.filter(
            period='MONTHLY'
        ).order_by('rank')[:100]
        serializer = LeaderboardSerializer(leaderboard, many=True)
        return Response(serializer.data)


class FriendsLeaderboardView(views.APIView):
    """Friends leaderboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # TODO: Implement friends relationship
        leaderboard = Leaderboard.objects.filter(
            period='ALL_TIME'
        ).order_by('rank')[:50]
        serializer = LeaderboardSerializer(leaderboard, many=True)
        return Response(serializer.data)
