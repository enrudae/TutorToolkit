from django.urls import path, include
from rest_framework import routers
from apps.notifications.views import NotificationViewSet

router = routers.DefaultRouter()
router.register('', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
]
