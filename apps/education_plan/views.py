from django.db.models import Q
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.education_plan.models import EducationPlan, Module
from apps.education_plan.serializers import EducationPlanSerializer, ModuleSerializer
from TutorToolkit.permissions import IsTutor, IsTutorCreator
from apps.education_plan.services import StudentInvitationService


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


class GetEducationPlan(ListAPIView):
    serializer_class = ModuleSerializer
    queryset = Module.objects.all()

    def get_object(self):
        user = self.request.user
        invitation_id = self.kwargs.get('plan_id')
        invitation = EducationPlan.objects.filter(
            Q(id=invitation_id) &
            Q(tutor=user.tutor) if user.role == 'tutor' else Q(student=user.student)
        ).first()

        if not invitation:
            raise Http404('Учебного плана с таким id не найдено')

        modules = invitation.module_set.all()
        return modules


class AddStudentToEducationPlan(APIView):
    def post(self, request, invite_code):
        if request.user.role != 'student':
            return Response({'detail': 'Приглашением может воспользоваться только студент.'},
                            status=status.HTTP_403_FORBIDDEN)

        student = request.user.student
        response = StudentInvitationService.add_student_to_education_plan(invite_code, student)
        return Response(response)
