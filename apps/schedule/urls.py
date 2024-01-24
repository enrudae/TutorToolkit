from django.urls import path, include
from rest_framework import routers
from apps.schedule.views import LessonViewSet

router = routers.DefaultRouter()
router.register('', LessonViewSet, basename='lesson')

urlpatterns = [
    path('', include(router.urls)),
]
