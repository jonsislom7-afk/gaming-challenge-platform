from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Notifications"""
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'is_read',
            'related_challenge', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
