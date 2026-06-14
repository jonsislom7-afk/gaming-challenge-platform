from django.contrib import admin
from .models import Leaderboard


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'period', 'rank', 'points', 'challenges_completed', 'updated_at']
    list_filter = ['period', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['updated_at']
    ordering = ['period', 'rank']
