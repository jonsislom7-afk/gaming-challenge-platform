from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = [
        ('CHALLENGER', 'Challenger'),
        ('STREAMER', 'Streamer'),
        ('ADMIN', 'Admin'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, default='Uzbekistan')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    total_points = models.IntegerField(default=0)
    is_email_verified = models.BooleanField(default=False)
    
    # Suspension/Ban system
    violation_count = models.IntegerField(default=0)  # Sokinish soni
    is_banned = models.BooleanField(default=False)
    ban_until = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"
    
    def check_and_apply_ban(self):
        """3 marta sokinsh → 2 hafta ban"""
        if self.violation_count >= 3:
            self.is_banned = True
            self.ban_until = timezone.now() + timedelta(days=14)
            self.save()
            return True
        return False


class EmailVerificationToken(models.Model):
    """Email verification token"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'email_verification_tokens'
    
    def is_valid(self):
        return timezone.now() < self.expires_at
