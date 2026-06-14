from django.contrib import admin
from .models import AIGeneratedIdea, AIIdeaFeedback


@admin.register(AIGeneratedIdea)
class AIGeneratedIdeaAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'game_category', 'difficulty', 'ai_model',
        'rating', 'views', 'premium_badge', 'created_at'
    ]
    list_filter = ['ai_model', 'difficulty', 'is_premium_only', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['rating', 'views', 'created_at', 'updated_at']
    
    def premium_badge(self, obj):
        if obj.is_premium_only:
            return '💎 Premium'
        return 'Free'
    premium_badge.short_description = 'Type'


@admin.register(AIIdeaFeedback)
class AIIdeaFeedbackAdmin(admin.ModelAdmin):
    list_display = ['ai_idea', 'user', 'is_liked_badge', 'created_at']
    list_filter = ['is_liked', 'created_at']
    search_fields = ['user__username', 'ai_idea__title']
    readonly_fields = ['created_at']
    
    def is_liked_badge(self, obj):
        if obj.is_liked:
            return '👍 Liked'
        return '👎 Disliked'
    is_liked_badge.short_description = 'Feedback'
