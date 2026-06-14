from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notifications'),
    path('<int:notification_id>/read/', views.NotificationMarkAsReadView.as_view(), name='mark-as-read'),
    path('mark-all-read/', views.NotificationMarkAllAsReadView.as_view(), name='mark-all-read'),
]
