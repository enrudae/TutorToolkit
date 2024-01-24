
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
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
        queryset = Lesson.objects.filter(
            Q(education_plan__tutor=user.tutor) if user.role == 'tutor' else Q(education_plan__student=user.student)
        )
        return queryset

    def get_serializer_class(self):
        if self.request.user.role == 'tutor':
            return LessonSerializerForTutorSerializer
        return LessonSerializerForStudentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsTutor()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTutorCreator()]
        return super().get_permissions()
