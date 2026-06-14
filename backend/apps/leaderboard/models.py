from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Leaderboard(models.Model):
    """Leaderboard model"""
    PERIOD_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('ALL_TIME', 'All Time'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='leaderboards',
        limit_choices_to={'role': 'STREAMER'}
    )
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    rank = models.IntegerField()
    points = models.IntegerField(default=0)
    challenges_completed = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaderboards'
        unique_together = ['user', 'period']
        ordering = ['period', 'rank']
    
    def __str__(self):
        return f"{self.user.username} - {self.period} (Rank: {self.rank})"
