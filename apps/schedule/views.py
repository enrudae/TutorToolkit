from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.notifications.tasks import send_lesson_notifications, send_notification
from apps.notifications.utils import delete_notification
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
        queryset = Lesson.objects.filter(Q(**{f'{profile_field}': profile}))
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
        message = f'Урок по предмету {lesson.education_plan.discipline} назначен на {lesson.date_start.strftime(" %d.%m %H:%M")}'
        notification_task_id = send_lesson_notifications.delay(lesson.id, message)
        lesson.notification_task_id = notification_task_id
        lesson.save()

    def perform_update(self, serializer):
        serializer.save()
        lesson = serializer.instance
        message = f'Урок по предмету {lesson.education_plan.discipline} перенесен на {lesson.date_start.strftime(" %d.%m %H:%M")}'
        send_notification.delay(lesson.education_plan.student.user.id, message)

        delete_notification(lesson.notification_task_id)

        message = f'Урок по предмету {lesson.education_plan.discipline} назначен на {lesson.date_start.strftime(" %d.%m %H:%M")}'
        notification_task_id = send_lesson_notifications.delay(lesson.id, message)
        lesson.notification_task_id = notification_task_id
        lesson.save()

    def perform_destroy(self, instance):
        delete_notification(instance.notification_task_id)
        message = f'Урок по предмету {instance.education_plan.discipline} {instance.date_start.strftime(" %d.%m %H:%M")} отменен'
        send_notification.delay(instance.education_plan.student.user.id, message)
        instance.delete()
