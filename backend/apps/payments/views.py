from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import Payment, SubscriptionPlan, UserSubscription, AdminPaymentVerification
from .serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    PaymentSerializer,
    CreatePaymentSerializer,
    AdminPaymentVerificationSerializer
)


class SubscriptionPlansView(views.APIView):
    """Get subscription plans by role"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        role = user.role  # CHALLENGER yoki STREAMER
        
        plans = SubscriptionPlan.objects.filter(
            role=role,
            is_active=True
        )
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data)


class UserSubscriptionView(views.APIView):
    """Get user's subscription status"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        subscription, created = UserSubscription.objects.get_or_create(user=user)
        
        # Subscription expire bo'lganmi tekshirish
        if subscription.is_active and subscription.is_expired():
            subscription.is_active = False
            subscription.save()
        
        serializer = UserSubscriptionSerializer(subscription)
        return Response(serializer.data)


class CreatePaymentView(views.APIView):
    """Create payment for subscription"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                plan = SubscriptionPlan.objects.get(
                    pk=serializer.validated_data['plan_id']
                )
            except SubscriptionPlan.DoesNotExist:
                return Response(
                    {'error': 'Plan not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Payment yaratish
            payment = Payment.objects.create(
                user=request.user,
                subscription_plan=plan,
                amount=plan.price,
                payment_method=serializer.validated_data['payment_method'],
                transaction_id=f'TXN_{request.user.id}_{plan.id}_{uuid.uuid4().hex[:8]}',
                status='CHECK_PENDING',  # Admin CHECK'ni kutish
                check_number=serializer.validated_data.get('check_number'),
                check_image=serializer.validated_data.get('check_image')
            )
            
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminVerifyPaymentView(views.APIView):
    """ADMIN - payment CHECK verification"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, payment_id):
        user = request.user
        
        if user.role != 'ADMIN':
            return Response(
                {'error': 'Only admins can verify payments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_verified = request.data.get('is_verified', False)
        rejection_reason = request.data.get('rejection_reason', '')
        
        verification, created = AdminPaymentVerification.objects.get_or_create(
            payment=payment,
            defaults={'admin': user}
        )
        
        if is_verified:
            payment.status = 'SUCCESS'
            payment.check_verified_by_admin = True
            payment.save()
            
            # Subscription activate qilish
            subscription = payment.user.subscription
            subscription.renew(payment.subscription_plan)
            
            # Ad-free option
            if request.data.get('is_ad_free', False):
                # +2000 som for ad-free (Streamer uchun)
                ad_free_payment = Payment.objects.create(
                    user=payment.user,
                    amount=2000,
                    payment_method=payment.payment_method,
                    transaction_id=f'ADFREE_{payment.transaction_id}',
                    status='SUCCESS',
                    description='Ad-free option'
                )
                subscription.is_ad_free = True
                subscription.save()
            
            verification.is_verified = True
            verification.verified_at = timezone.now()
        else:
            payment.status = 'FAILED'
            payment.save()
            verification.rejection_reason = rejection_reason
        
        verification.save()
        
        return Response(
            AdminPaymentVerificationSerializer(verification).data
        )


class AdminPendingPaymentsView(views.APIView):
    """ADMIN - pending payments (CHECK'ni kutish)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'ADMIN':
            return Response(
                {'error': 'Only admins can view this'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_payments = Payment.objects.filter(
            status='CHECK_PENDING'
        ).order_by('-created_at')
        serializer = PaymentSerializer(pending_payments, many=True)
        return Response(serializer.data)
