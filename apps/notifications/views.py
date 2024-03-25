from django.db.models import Q, F, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.notifications.models import Notification
from apps.education_plan.models import EducationPlan
from apps.notifications.serializers import NotificationSerializer
from TutorToolkit.permissions import IsTutor


class NotificationViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user.userprofile)
        return queryset
