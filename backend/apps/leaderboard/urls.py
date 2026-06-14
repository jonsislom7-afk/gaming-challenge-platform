from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.LeaderboardViewSet, basename='leaderboard')

urlpatterns = [
    path('global/', views.GlobalLeaderboardView.as_view(), name='global-leaderboard'),
    path('monthly/', views.MonthlyLeaderboardView.as_view(), name='monthly-leaderboard'),
    path('friends/', views.FriendsLeaderboardView.as_view(), name='friends-leaderboard'),
] + router.urls
