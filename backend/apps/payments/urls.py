from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.SubscriptionPlansView.as_view(), name='plans'),
    path('subscription/', views.UserSubscriptionView.as_view(), name='subscription'),
    path('create/', views.CreatePaymentView.as_view(), name='create-payment'),
    path('admin/verify/<int:payment_id>/', views.AdminVerifyPaymentView.as_view(), name='verify-payment'),
    path('admin/pending/', views.AdminPendingPaymentsView.as_view(), name='pending-payments'),
]
