from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.notifications.services import NotificationService
from apps.schedule.models import Lesson
from apps.education_plan.models import EducationPlan
from apps.schedule.serializers import LessonSerializerForTutorSerializer, LessonSerializerForStudentSerializer
from TutorToolkit.permissions import IsTutor, IsTutorCreator


class LessonViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = LessonSerializerForStudentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        profile = user.userprofile
        profile_field = profile.role
        plans = EducationPlan.objects.filter(Q(**{f'{profile_field}': profile}))
        queryset = Lesson.objects.filter(education_plan__in=plans, is_canceled=False)
        return queryset

    def get_serializer_class(self):
        if self.request.user.userprofile.role == 'tutor':
            return LessonSerializerForTutorSerializer
        return LessonSerializerForStudentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsTutor()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTutorCreator()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save()
        lesson = serializer.instance
        NotificationService.handle_lesson_reminder(lesson.education_plan, lesson)
        lesson.save()

    def perform_destroy(self, instance):
        NotificationService.handle_canceling(instance.education_plan, instance)
        instance.is_canceled = True
        instance.save()

    def perform_update(self, serializer):
        original_date_start = serializer.instance.date_start
        serializer.save()
        updated_lesson = serializer.instance

        if original_date_start != updated_lesson.date_start:
            NotificationService.handle_rescheduling(updated_lesson.education_plan, updated_lesson)
