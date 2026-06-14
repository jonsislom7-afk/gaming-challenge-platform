from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Subscription plans"""
    ROLE_CHOICES = [
        ('CHALLENGER', 'Challenger'),
        ('STREAMER', 'Streamer'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='UZS')
    duration_days = models.IntegerField()  # 5 kun, 30 kun, etc.
    
    # Features
    daily_challenge_limit = models.IntegerField(null=True, blank=True)  # Challenger uchun
    has_ads = models.BooleanField(default=True)  # Streamer uchun
    premium_challenges = models.BooleanField(default=False)  # Streamer uchun
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        unique_together = ['name', 'role']
    
    def __str__(self):
        return f"{self.name} ({self.role}) - {self.price} UZS"


class UserSubscription(models.Model):
    """User subscription status"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Streamer uchun qo'shimcha
    is_ad_free = models.BooleanField(default=False)  # +2000 som
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
    
    def __str__(self):
        return f"{self.user.username} - {self.plan}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def renew(self, plan):
        """Subscription yangilash"""
        self.plan = plan
        self.started_at = timezone.now()
        self.expires_at = timezone.now() + timedelta(days=plan.duration_days)
        self.is_active = True
        self.save()


class Payment(models.Model):
    """Payment transactions"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CHECK_PENDING', 'Check Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('HUMO', 'Humo Card'),
        ('UZCARD', 'UZCard'),
        ('VISA', 'Visa'),
        ('PAYME', 'Payme'),
        ('CLICK', 'Click'),
        ('UZUM', 'UZUM Bank'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='UZS')
    status = models.CharField(max_digits=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # CHECK system (Admin uchun)
    check_number = models.CharField(max_length=255, blank=True, null=True)
    check_image = models.ImageField(upload_to='checks/', blank=True, null=True)
    check_verified_by_admin = models.BooleanField(default=False)
    
    transaction_id = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} UZS ({self.status})"


class AdminPaymentVerification(models.Model):
    """Admin CHECK verification"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    admin = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'ADMIN'}
    )
    
    is_verified = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_payment_verifications'
    
    def __str__(self):
        return f"Payment #{self.payment.id} - {'Verified' if self.is_verified else 'Pending'}"
