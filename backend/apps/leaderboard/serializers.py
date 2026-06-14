from rest_framework import serializers
from apps.leaderboard.models import Leaderboard
from apps.accounts.serializers import UserBasicSerializer


class LeaderboardSerializer(serializers.ModelSerializer):
    """Leaderboard"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'user', 'period', 'rank', 'points',
            'challenges_completed', 'updated_at'
        ]
