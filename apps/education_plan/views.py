from django.db.models import Q, F, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.education_plan.models import EducationPlan, Module, Card, Label
from apps.education_plan.serializers import EducationPlanSerializer, ModuleSerializer, ModulesInEducationPlanSerializer, \
    CardSerializer, LabelSerializer, EducationPlanForStudentSerializer, EducationPlanForTutorSerializer, \
    MoveElementSerializer
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


class GetInviteInfoByCode(APIView):
    def get(self, request, invite_code):
        plan, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)
        if error_response:
            return Response(data=error_response, status=status_code)

        data = {
            'first_name': plan.tutor.first_name,
            'last_name': plan.tutor.last_name,
            'discipline': plan.discipline,
        }

        return Response(data=data, status=status.HTTP_200_OK)


class GetUsersData(APIView):
    permission_classes = [IsAuthenticated]

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


class AddStudentToTeacherByInviteCode(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invite_code):
        user = self.request.user
        if user.role != 'student':
            return Response(status=status.HTTP_403_FORBIDDEN)

        _, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)
        if error_response:
            return Response(data=error_response, status=status_code)

        StudentInvitationService.add_student_to_education_plan(invite_code, user.student)

        return Response(status=status.HTTP_201_CREATED)


def move_card(card, destination_index, destination_module):
    source_module = card.module
    source_index = card.index
    cards_in_source = source_module.cards
    cards_in_destination = destination_module.cards.all()
    destination_index = min(destination_index, len(cards_in_destination))

    cards_to_move = cards_in_source.filter(index__gt=source_index)
    if cards_to_move:
        cards_to_move.update(index=F('index') - 1)

    cards_to_move = cards_in_destination.filter(index__gte=destination_index)
    if cards_to_move:
        cards_to_move.update(index=F('index') + 1)

    card.index = destination_index
    card.module = destination_module
    card.save()


class ChangeOrderOfElements(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = self.request.user
        if user.role == 'student':
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = MoveElementSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            element_type = validated_data.get('element_type')
            element_id = validated_data.get('element_id')
            destination_index = validated_data.get('destination_index')
            destination_id = validated_data.get('destination_id', None)

            card = get_object_or_404(Card, id=element_id, module__plan__tutor=user.tutor)
            destination_module = get_object_or_404(Module, id=destination_id, plan__tutor=user.tutor)
            move_card(card, destination_index, destination_module)

            serializer = ModulesInEducationPlanSerializer(destination_module.plan)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class test_send(APIView):
    def get(self, request):
        from apps.notifications.tasks import send_notification
        id = send_notification.delay(request.user.id, 'тест').id
        return Response(data={'id': id}, status=status.HTTP_200_OK)
