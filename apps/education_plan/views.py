from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets
from apps.education_plan.models import EducationPlan
from apps.education_plan.serializers import EducationPlanSerializer
from TutorToolkit.permissions import IsTutor, IsTutorCreator


class EducationPlanViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = EducationPlanSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = EducationPlan.objects.filter(
            Q(tutor=user.tutor) if user.role == 'tutor' else Q(student=user.student)
        )
        return queryset

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsTutor()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTutorCreator()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        tutor = user.tutor
        serializer.save(tutor=tutor)

