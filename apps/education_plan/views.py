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


class LabelViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = LabelSerializer
    permission_classes = (IsTutor,)

    def get_queryset(self):
        user = self.request.user
        queryset = Label.objects.filter(tutor__user=user)
        return queryset


class CheckPossibilityOfAddingByInviteCode(APIView):
    def post(self, request, invite_code):
        plan, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)
        if error_response:
            return Response(data=error_response, status=status_code)

        return Response(data={'tutor': f'{plan.tutor.last_name} {plan.tutor.first_name}'}, status=status.HTTP_200_OK)
