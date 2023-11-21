from django.db.models import Q, Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.education_plan.models import EducationPlan, Module, Card, Label
from apps.education_plan.serializers import EducationPlanSerializer, ModuleSerializer, ModulesInEducationPlanSerializer, \
    CardSerializer, LabelSerializer
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
        ).prefetch_related('modules', 'modules__cards', 'modules__cards__labels')
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


class ModuleViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ModuleSerializer
    permission_classes = (IsTutor,)

    def get_queryset(self):
        user = self.request.user
        queryset = Module.objects.filter(plan__tutor__user=user)
        return queryset


class CardViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = CardSerializer
    permission_classes = (IsTutor,)

    def get_queryset(self):
        user = self.request.user
        queryset = Card.objects.filter(module__plan__tutor__user=user)
        return queryset

#
# class LabelViewSet(mixins.ListModelMixin,
#                    mixins.CreateModelMixin,
#                    mixins.UpdateModelMixin,
#                    mixins.DestroyModelMixin,
#                    viewsets.GenericViewSet):
#     serializer_class = LabelSerializer
#     permission_classes = (IsTutor,)
#
#     def get_queryset(self):
#         user = self.request.user
#         queryset = Label.objects.filter()
#         return queryset


class AddStudentToEducationPlan(APIView):
    def post(self, request, invite_code):
        if request.user.role != 'student':
            return Response({'detail': 'Приглашением может воспользоваться только студент.'},
                            status=status.HTTP_403_FORBIDDEN)

        student = request.user.student
        response = StudentInvitationService.add_student_to_education_plan(invite_code, student)
        return Response(response)
