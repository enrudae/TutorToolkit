from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.education_plan.models import EducationPlan
from apps.education_plan.serializers import EducationPlanSerializer, ModulesInEducationPlanSerializer
from TutorToolkit.permissions import IsTutor, IsTutorCreator
from apps.education_plan.services import StudentInvitationService


class EducationPlanViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = EducationPlanSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = EducationPlan.objects.filter(
            Q(tutor=user.tutor) if user.role == 'tutor' else Q(student=user.student)
        )
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        tutor = user.tutor
        serializer.save(tutor=tutor)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsTutor()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTutorCreator()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModulesInEducationPlanSerializer
        return EducationPlanSerializer


class AddStudentToEducationPlan(APIView):
    def post(self, request, invite_code):
        if request.user.role != 'student':
            return Response({'detail': 'Приглашением может воспользоваться только студент.'},
                            status=status.HTTP_403_FORBIDDEN)

        student = request.user.student
        response = StudentInvitationService.add_student_to_education_plan(invite_code, student)
        return Response(response)
