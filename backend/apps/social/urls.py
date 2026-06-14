from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'ai-ideas', views.AIGeneratedIdeasViewSet, basename='ai-ideas')

urlpatterns = [
    path('ai-ideas-list/', views.AIIdeasListView.as_view(), name='ai-ideas-list'),
] + router.urls
