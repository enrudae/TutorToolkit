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
        profile_field = user.role
        profile = getattr(user, profile_field, None)

        if not profile:
            return Response(status=status.HTTP_404_NOT_FOUND)

        education_plans = EducationPlan.objects.filter(
            Q(**{f'{profile_field}': profile})
        ).only('id', 'status', 'discipline', 'student_first_name', 'student_last_name', 'tutor').select_related('tutor')

        queryset = Notification.objects.filter(education_plan__in=education_plans)
        return queryset
