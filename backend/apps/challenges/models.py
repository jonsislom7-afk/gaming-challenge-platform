from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class GameCategory(models.Model):
    """Game categories (dunyadagi oyinlar)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'game_categories'
        verbose_name_plural = 'Game Categories'
    
    def __str__(self):
        return self.name


class Challenge(models.Model):
    """Gaming challenge model"""
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
        ('EXPERT', 'Expert'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ACTIVE', 'Active'),
    ]
    
    # Challenger ma'lumotlari
    challenger = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_challenges',
        limit_choices_to={'role': 'CHALLENGER'}
    )
    
    # Challenge tafsilotlari
    title = models.CharField(max_length=200)
    description = models.TextField()
    game_category = models.ForeignKey(
        GameCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    reward_points = models.IntegerField(default=100)
    
    # Rasm/Video
    image = models.ImageField(upload_to='challenges/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    
    # Premium flag
    is_premium_only = models.BooleanField(
        default=False, 
        help_text="Eng yaxshi idealar - faqat premium uchun"
    )
    
    # Status va limits
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    max_participants = models.IntegerField(default=1000)
    current_participants = models.IntegerField(default=0)
    
    # AI generated flag
    is_ai_generated = models.BooleanField(default=False)
    ai_model = models.CharField(max_length=50, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'challenges'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['is_premium_only']),
        ]
    
    def __str__(self):
        return self.title


class DailyChallenge(models.Model):
    """Har kuni boshqa challenge - daily rotation"""
    challenge = models.ForeignKey(
        Challenge, 
        on_delete=models.CASCADE, 
        related_name='daily_instances'
    )
    date = models.DateField(auto_now_add=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_challenges'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.challenge.title} - {self.date}"


class UserChallenge(models.Model):
    """User's challenge attempt/completion"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='challenge_attempts',
        limit_choices_to={'role': 'STREAMER'}
    )
    challenge = models.ForeignKey(
        Challenge, 
        on_delete=models.CASCADE, 
        related_name='user_attempts'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    score = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    
    submission_proof = models.URLField(blank=True, null=True)  # Video yoki screenshot link
    
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'user_challenges'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"


class ChallengerViolation(models.Model):
    """Challenger sokinishi/violations"""
    VIOLATION_TYPES = [
        ('INAPPROPRIATE_CONTENT', 'Inappropriate Content'),
        ('DUPLICATE', 'Duplicate Challenge'),
        ('LOW_QUALITY', 'Low Quality'),
        ('SCAM', 'Scam/Fraud'),
        ('OTHER', 'Other'),
    ]
    
    challenger = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='violations',
        limit_choices_to={'role': 'CHALLENGER'}
    )
    challenge = models.ForeignKey(
        Challenge, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    violation_type = models.CharField(max_length=50, choices=VIOLATION_TYPES)
    description = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'challenger_violations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.challenger.username} - {self.violation_type}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Violation count yangilash
        self.challenger.violation_count += 1
        self.challenger.check_and_apply_ban()
