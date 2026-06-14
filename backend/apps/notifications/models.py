from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('CHALLENGE_NEW', 'New Challenge'),
        ('CHALLENGE_COMPLETED', 'Challenge Completed'),
        ('PAYMENT_SUCCESS', 'Payment Success'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('BAN', 'Account Banned'),
        ('ACHIEVEMENT', 'Achievement'),
        ('MESSAGE', 'Message'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    
    related_challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
