from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.education_plan.models import EducationPlan, Module, Card, Label
from apps.education_plan.serializers import EducationPlanSerializer, ModuleSerializer, ModulesInEducationPlanSerializer, \
    CardSerializer, LabelSerializer, EducationPlanForStudentSerializer, EducationPlanForTutorSerializer
from TutorToolkit.permissions import IsTutor, IsTutorCreator
from apps.education_plan.services import StudentInvitationService
from apps.account.serializers import ProfileSerializer


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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        email = request.data.get('email')
        user_status = 'active' if StudentInvitationService.check_email_exists(email) else 'inactive'
        response.data['user_status'] = user_status
        return response

    def perform_create(self, serializer):
        user = self.request.user
        tutor = user.tutor
        serializer.save(tutor=tutor)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsTutor()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTutorCreator()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
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

    def perform_create(self, serializer):
        plan_id = self.request.data.get('plan_id')
        education_plan = get_object_or_404(EducationPlan, pk=plan_id)
        serializer.save(plan=education_plan)


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

    def perform_create(self, serializer):
        module_id = self.request.data.get('module_id')
        module = get_object_or_404(Module, pk=module_id)
        serializer.save(module=module)


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

    def perform_create(self, serializer):
        user = self.request.user
        tutor = user.tutor
        serializer.save(tutor=tutor)


class CheckPossibilityOfAddingByInviteCode(APIView):
    def post(self, request, invite_code):
        plan, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)
        if error_response:
            return Response(data=error_response, status=status_code)

        return Response(data={'tutor': f'{plan.tutor.last_name} {plan.tutor.first_name}'}, status=status.HTTP_200_OK)


class GetUsersData(APIView):
    def get(self, request):

        user = self.request.user
        profile_field = user.role
        profile = getattr(user, profile_field, None)

        if not profile:
            return Response(status=status.HTTP_404_NOT_FOUND)

        profile_serializer = ProfileSerializer(profile)

        education_plans = EducationPlan.objects.filter(
            Q(**{f'{profile_field}': profile})
        ).only('id', 'status', 'discipline', 'student_first_name', 'student_last_name', 'tutor').select_related('tutor')

        if profile_field == 'tutor':
            education_plans_serializer = EducationPlanForTutorSerializer(education_plans, many=True)
        else:
            education_plans_serializer = EducationPlanForStudentSerializer(education_plans, many=True)

        response_data = {
            **profile_serializer.data,
            'plans': education_plans_serializer.data
        }

        return Response(response_data)
