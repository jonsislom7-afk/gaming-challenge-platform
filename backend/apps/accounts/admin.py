from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CustomUser, EmailVerificationToken


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'role_badge', 'total_points',
        'is_email_verified', 'ban_status', 'violation_count'
    ]
    list_filter = ['role', 'is_banned', 'is_email_verified', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = [
        'id', 'total_points', 'violation_count', 'is_banned',
        'ban_until', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('User Info', {
            'fields': ('username', 'email', 'password', 'first_name', 'last_name')
        }),
        ('Profile', {
            'fields': ('avatar', 'bio', 'gender', 'birth_date', 'country', 'phone')
        }),
        ('Account Status', {
            'fields': ('role', 'is_email_verified', 'is_active')
        }),
        ('Points & Violations', {
            'fields': ('total_points', 'violation_count')
        }),
        ('Ban System', {
            'fields': ('is_banned', 'ban_until')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def role_badge(self, obj):
        colors = {
            'CHALLENGER': '#3498db',  # Blue
            'STREAMER': '#e74c3c',    # Red
            'ADMIN': '#2ecc71',       # Green
        }
        color = colors.get(obj.role, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    def ban_status(self, obj):
        if obj.is_banned:
            return format_html(
                '<span style="color: red; font-weight: bold;">🔒 BANNED until {}</span>',
                obj.ban_until.strftime('%Y-%m-%d') if obj.ban_until else 'Unknown'
            )
        return format_html('<span style="color: green;">✓ Active</span>')
    ban_status.short_description = 'Ban Status'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_valid_badge', 'created_at', 'expires_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'created_at']
    
    def is_valid_badge(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Expired</span>')
    is_valid_badge.short_description = 'Status'
