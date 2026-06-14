from rest_framework import serializers
from apps.payments.models import Payment, SubscriptionPlan, UserSubscription, AdminPaymentVerification


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Subscription plans"""
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'role', 'description', 'price', 'currency',
            'duration_days', 'daily_challenge_limit', 'has_ads',
            'premium_challenges'
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """User subscription status"""
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = ['id', 'plan', 'is_active', 'is_ad_free', 'started_at', 'expires_at']
        read_only_fields = ['id', 'started_at', 'expires_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Payment transaction"""
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'status', 'payment_method',
            'check_number', 'check_image', 'check_verified_by_admin',
            'transaction_id', 'created_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'status', 'check_verified_by_admin', 'created_at']


class CreatePaymentSerializer(serializers.Serializer):
    """Create payment"""
    plan_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=['HUMO', 'UZCARD', 'VISA', 'PAYME', 'CLICK', 'UZUM']
    )
    check_number = serializers.CharField(max_length=255, required=False)
    check_image = serializers.ImageField(required=False)
    
    def validate_plan_id(self, value):
        try:
            SubscriptionPlan.objects.get(pk=value)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Plan not found")
        return value


class AdminPaymentVerificationSerializer(serializers.ModelSerializer):
    """Admin payment verification (CHECK)"""
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = AdminPaymentVerification
        fields = ['id', 'payment', 'is_verified', 'rejection_reason', 'verified_at']
        read_only_fields = ['id', 'verified_at']
