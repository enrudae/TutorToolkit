from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.notifications.tasks import send_notification
# from apps.notifications.utils import delete_notification
from apps.schedule.models import Lesson
from apps.education_plan.models import EducationPlan
from apps.schedule.serializers import LessonSerializerForTutorSerializer, LessonSerializerForStudentSerializer
from TutorToolkit.permissions import IsTutor, IsTutorCreator
from apps.notifications.models import Notification


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
        queryset = Lesson.objects.filter(education_plan__in=plans)
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
        Notification.create_notification(lesson.education_plan, 'info', lesson=lesson)
        lesson.save()

    def perform_destroy(self, instance):
        Notification.create_notification(instance.education_plan, 'canceling', lesson=instance)
        instance.is_cancelled = True
        instance.save()

    def perform_update(self, serializer):
        print('11111111111111111111')
        serializer.save()
        lesson = serializer.instance
        Notification.cancel_lesson_notification(lesson)
        Notification.create_notification(lesson.education_plan, 'rescheduling', lesson=lesson)
        # serializer.is_cancelled = True
        # serializer.save()
