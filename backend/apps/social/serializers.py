from rest_framework import serializers
from apps.social.models import AIGeneratedIdea, AIIdeaFeedback


class AIGeneratedIdeaSerializer(serializers.ModelSerializer):
    """AI generated ideas"""
    class Meta:
        model = AIGeneratedIdea
        fields = [
            'id', 'title', 'description', 'game_category', 'difficulty',
            'ai_model', 'rating', 'views', 'is_premium_only', 'created_at'
        ]
        read_only_fields = ['id', 'rating', 'views', 'created_at']


class AIIdeaFeedbackSerializer(serializers.ModelSerializer):
    """AI idea feedback/rating"""
    class Meta:
        model = AIIdeaFeedback
        fields = ['id', 'ai_idea', 'is_liked', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']
