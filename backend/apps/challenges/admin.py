from django.contrib import admin
from django.utils.html import format_html
from .models import Challenge, DailyChallenge, UserChallenge, ChallengerViolation, GameCategory


@admin.register(GameCategory)
class GameCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'challenger', 'difficulty_badge', 'status_badge',
        'premium_badge', 'ai_badge', 'current_participants', 'created_at'
    ]
    list_filter = ['status', 'difficulty', 'is_premium_only', 'is_ai_generated', 'created_at']
    search_fields = ['title', 'description', 'challenger__username']
    readonly_fields = ['id', 'current_participants', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Challenge Info', {
            'fields': ('title', 'description', 'challenger', 'game_category')
        }),
        ('Details', {
            'fields': ('difficulty', 'reward_points', 'max_participants', 'current_participants')
        }),
        ('Media', {
            'fields': ('image', 'video_url')
        }),
        ('Settings', {
            'fields': ('is_premium_only', 'is_ai_generated', 'ai_model')
        }),
        ('Status & Approval', {
            'fields': ('status', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def difficulty_badge(self, obj):
        colors = {
            'EASY': '#2ecc71',
            'MEDIUM': '#f39c12',
            'HARD': '#e74c3c',
            'EXPERT': '#8e44ad',
        }
        color = colors.get(obj.difficulty, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_difficulty_display()
        )
    difficulty_badge.short_description = 'Difficulty'
    
    def status_badge(self, obj):
        colors = {
            'DRAFT': '#95a5a6',
            'PENDING': '#f39c12',
            'APPROVED': '#2ecc71',
            'REJECTED': '#e74c3c',
            'ACTIVE': '#3498db',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def premium_badge(self, obj):
        if obj.is_premium_only:
            return format_html('<span style="color: gold; font-weight: bold;">💎 Premium</span>')
        return format_html('<span style="color: gray;">Free</span>')
    premium_badge.short_description = 'Type'
    
    def ai_badge(self, obj):
        if obj.is_ai_generated:
            return format_html('<span style="color: purple; font-weight: bold;">🤖 AI</span>')
        return ''
    ai_badge.short_description = 'AI'


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'date', 'created_at']
    list_filter = ['date']
    search_fields = ['challenge__title']
    readonly_fields = ['created_at']


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'challenge', 'status_badge', 'score',
        'points_earned', 'submitted_at', 'completed_at'
    ]
    list_filter = ['status', 'started_at', 'completed_at']
    search_fields = ['user__username', 'challenge__title']
    readonly_fields = ['started_at', 'submitted_at', 'completed_at']
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#95a5a6',
            'IN_PROGRESS': '#3498db',
            'SUBMITTED': '#f39c12',
            'COMPLETED': '#2ecc71',
            'FAILED': '#e74c3c',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ChallengerViolation)
class ChallengerViolationAdmin(admin.ModelAdmin):
    list_display = [
        'challenger', 'violation_type', 'challenge',
        'created_at', 'violation_count_badge'
    ]
    list_filter = ['violation_type', 'created_at']
    search_fields = ['challenger__username', 'challenge__title']
    readonly_fields = ['created_at']
    
    def violation_count_badge(self, obj):
        count = obj.challenger.violation_count
        if count >= 3:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">🔒 {}/3 BAN</span>',
                count
            )
        return format_html(
            '<span style="background-color: #f39c12; color: white; padding: 3px 8px; border-radius: 3px;">{}/3</span>',
            count
        )
    violation_count_badge.short_description = 'Violations'
