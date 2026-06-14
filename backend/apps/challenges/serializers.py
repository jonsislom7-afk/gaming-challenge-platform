from rest_framework import serializers
from apps.challenges.models import Challenge, DailyChallenge, UserChallenge, ChallengerViolation, GameCategory
from apps.accounts.serializers import UserBasicSerializer


class GameCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GameCategory
        fields = ['id', 'name', 'description', 'image']


class ChallengeSerializer(serializers.ModelSerializer):
    """Challenge listing and detail"""
    challenger = UserBasicSerializer(read_only=True)
    game_category = GameCategorySerializer(read_only=True)
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'challenger', 'game_category',
            'difficulty', 'reward_points', 'image', 'video_url',
            'is_premium_only', 'is_ai_generated', 'current_participants',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'current_participants', 'created_at']


class CreateChallengeSerializer(serializers.ModelSerializer):
    """Create new challenge (Challenger uchun)"""
    class Meta:
        model = Challenge
        fields = [
            'title', 'description', 'game_category', 'difficulty',
            'reward_points', 'image', 'video_url', 'max_participants'
        ]
    
    def create(self, validated_data):
        validated_data['challenger'] = self.context['request'].user
        validated_data['status'] = 'PENDING'  # Admin tasdig'i kerak
        return Challenge.objects.create(**validated_data)


class DailyChallengeSerializer(serializers.ModelSerializer):
    """Daily challenge"""
    challenge = ChallengeSerializer(read_only=True)
    
    class Meta:
        model = DailyChallenge
        fields = ['id', 'challenge', 'date']


class UserChallengeSerializer(serializers.ModelSerializer):
    """User's challenge attempt"""
    challenge = ChallengeSerializer(read_only=True)
    
    class Meta:
        model = UserChallenge
        fields = [
            'id', 'challenge', 'status', 'score', 'points_earned',
            'submission_proof', 'started_at', 'submitted_at', 'completed_at'
        ]
        read_only_fields = ['id', 'points_earned', 'started_at']


class SubmitChallengeSerializer(serializers.ModelSerializer):
    """Submit challenge completion"""
    class Meta:
        model = UserChallenge
        fields = ['score', 'submission_proof']


class ChallengerViolationSerializer(serializers.ModelSerializer):
    """Challenge violation (Admin uchun)"""
    class Meta:
        model = ChallengerViolation
        fields = ['id', 'challenger', 'challenge', 'violation_type', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']
