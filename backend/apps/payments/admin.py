from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, SubscriptionPlan, UserSubscription, AdminPaymentVerification


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'price_display', 'duration_days', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['name', 'description']
    
    def price_display(self, obj):
        return f"{obj.price:,.0f} {obj.currency}"
    price_display.short_description = 'Price'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'plan', 'status_badge',
        'is_ad_free', 'started_at', 'expires_at'
    ]
    list_filter = ['is_active', 'is_ad_free', 'started_at']
    search_fields = ['user__username']
    readonly_fields = ['started_at', 'expires_at']
    
    def status_badge(self, obj):
        if obj.is_active:
            if obj.is_expired():
                return format_html('<span style="color: red;">✗ Expired</span>')
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: gray;">Inactive</span>')
    status_badge.short_description = 'Status'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'amount_display', 'status_badge',
        'payment_method', 'check_verified_badge', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'transaction_id']
    readonly_fields = [
        'id', 'transaction_id', 'created_at', 'updated_at',
        'check_image_display'
    ]
    
    fieldsets = (
        ('User & Plan', {
            'fields': ('user', 'subscription_plan')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'payment_method', 'transaction_id')
        }),
        ('CHECK System', {
            'fields': ('check_number', 'check_image_display', 'check_verified_by_admin')
        }),
        ('Status', {
            'fields': ('status', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        return f"{obj.amount:,.0f} {obj.currency}"
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#95a5a6',
            'CHECK_PENDING': '#f39c12',
            'SUCCESS': '#2ecc71',
            'FAILED': '#e74c3c',
            'CANCELLED': '#95a5a6',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def check_verified_badge(self, obj):
        if obj.check_verified_by_admin:
            return format_html('<span style="color: green; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: red;">✗ Not Verified</span>')
    check_verified_badge.short_description = 'CHECK Status'
    
    def check_image_display(self, obj):
        if obj.check_image:
            return format_html(
                '<img src="{}" width="200" height="auto" />',
                obj.check_image.url
            )
        return 'No image'
    check_image_display.short_description = 'CHECK Image'


@admin.register(AdminPaymentVerification)
class AdminPaymentVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'payment', 'admin', 'is_verified_badge',
        'verified_at'
    ]
    list_filter = ['is_verified', 'verified_at']
    search_fields = ['payment__transaction_id', 'admin__username']
    readonly_fields = ['verified_at']
    
    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: red;">✗ Rejected</span>')
    is_verified_badge.short_description = 'Status'
