from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'title', 'is_read_badge', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    
    def is_read_badge(self, obj):
        if obj.is_read:
            return '✓ Read'
        return '✗ Unread'
    is_read_badge.short_description = 'Status'
