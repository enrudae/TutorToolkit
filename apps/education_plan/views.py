from django.db.models import Q, F, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from apps.education_plan.models import EducationPlan, Module, Card, Label, File, CardContent, SectionContent
from apps.education_plan.serializers import EducationPlanSerializer, ModuleSerializer, ModulesInEducationPlanSerializer, \
    CardSerializer, LabelSerializer, EducationPlanForStudentSerializer, EducationPlanForTutorSerializer, \
    MoveElementSerializer, FileSerializer, CardContentSerializer, SectionContentSerializer
from TutorToolkit.permissions import IsTutor, IsStudent, IsTutorCreator
from apps.education_plan.services import StudentInvitationService, MoveElementService
from apps.account.serializers import ProfileSerializer
from apps.notifications.models import Notification


class EducationPlanViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = EducationPlanSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        profile = user.userprofile
        profile_field = profile.role
        queryset = EducationPlan.objects.filter(
            Q(**{f'{profile_field}': profile})
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
        email = serializer.context['request'].data.get('email')
        if EducationPlan.objects.filter(tutor=user.userprofile, student_email=email).exists():
            raise ValidationError({"email": "Студент с этим email уже приглашен к этому учителю."})

        plan = serializer.save(tutor=user.userprofile, student_email=email)
        if StudentInvitationService.check_email_exists(email):
            Notification.create_notification(plan, 'invite', email=email)

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
        queryset = Card.objects.filter(module__plan__tutor__user=user, is_template=False)
        return queryset

    def perform_create(self, serializer):
        module_id = self.request.data.get('module_id')
        module = get_object_or_404(Module, pk=module_id)
        card = serializer.save(module=module)
        CardContent.objects.create(card=card)

    @action(detail=True, methods=['post'])
    def create_template(self, request, pk=None):
        card = get_object_or_404(Card, pk=pk)
        template = card.create_template()
        return Response(CardSerializer(template).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def templates(self, request):
        templates = Card.objects.filter(is_template=True)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_card_from_template(self, request, pk=None):
        template = get_object_or_404(Card, pk=pk)
        if not template.is_template:
            return Response({"detail": "Only templates can be used to create new cards."},
                            status=status.HTTP_400_BAD_REQUEST)

        module_id = request.data.get('module_id')
        module = get_object_or_404(Module, pk=module_id)
        new_card = template.create_card_from_template(module)
        return Response(CardSerializer(new_card).data, status=status.HTTP_201_CREATED)


class CardContentViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = CardContentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_profile = self.request.user.userprofile
        if user_profile.role == 'tutor':
            return CardContent.objects.filter(card__module__plan__tutor=user_profile)
        return CardContent.objects.filter(card__module__plan__student=user_profile)

    def perform_create(self, serializer):
        card_id = self.request.data.get('card_id')
        card = get_object_or_404(Card, pk=card_id)
        serializer.save(card=card)

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsTutor()]
        return super().get_permissions()

    @action(detail=True, methods=['patch'], url_path='update-section/(?P<section_type>homework|lesson|repetition)')
    def update_section(self, request, pk=None, section_type=None):
        card_content = self.get_object()
        section_content = getattr(card_content, section_type)

        if section_content is None:
            section_content = SectionContent.objects.create(text="")
            setattr(card_content, section_type, section_content)
            card_content.save()

        serializer = SectionContentSerializer(section_content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        serializer.save(tutor=user.userprofile)


class GetInviteInfoByCode(APIView):
    def get(self, request, invite_code):
        plan, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)
        if error_response:
            return Response(data=error_response, status=status_code)

        data = {
            'first_name': plan.tutor.first_name,
            'last_name': plan.tutor.last_name,
            'discipline': plan.discipline,
            'student_email': plan.student_email,
        }

        return Response(data=data, status=status.HTTP_200_OK)


class GetUsersData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получение информации по текущему пользователю и всем прикрепленным к нему ученикам/учителям."""
        user = self.request.user
        profile = user.userprofile
        profile_field = profile.role

        if not profile:
            return Response(status=status.HTTP_404_NOT_FOUND)

        profile_serializer = ProfileSerializer(profile)

        education_plans = EducationPlan.objects.filter(Q(**{f'{profile_field}': profile})
                                                       ).only('id', 'status', 'discipline', 'student_first_name',
                                                              'student_last_name', 'tutor').select_related('tutor')

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
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        """Подтверждение приглашения учителя."""
        user = self.request.user
        profile = user.userprofile
        invite_code = request.data.get('invite_code')
        if not invite_code:
            return Response(data={'error': 'invite_code is required'}, status=status.HTTP_400_BAD_REQUEST)

        _, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)
        if error_response:
            return Response(data=error_response, status=status_code)

        StudentInvitationService.add_student_to_education_plan(invite_code, profile)

        return Response(status=status.HTTP_201_CREATED)


class ChangeOrderOfElements(APIView):
    permission_classes = [IsAuthenticated, IsTutor]

    def post(self, request):
        """Изменение порядка элементов (модуля, карточки)."""
        user = self.request.user
        profile = user.userprofile

        serializer = MoveElementSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            element_type = validated_data.get('element_type')
            element_id = validated_data.get('element_id')
            destination_index = validated_data.get('destination_index')
            destination_id = validated_data.get('destination_id', None)

            if element_type == 'task':
                card = get_object_or_404(Card, id=element_id, module__plan__tutor=profile)
                module = get_object_or_404(Module, id=destination_id, plan__tutor=profile)
                MoveElementService.move_card(card, destination_index, module)
                serializer = CardSerializer(card)
            else:
                module = get_object_or_404(Module, id=element_id, plan__tutor=profile)
                MoveElementService.move_module(module, destination_index)
                serializer = ModuleSerializer(module)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TutorFilesView(APIView):
    permission_classes = [IsAuthenticated, IsTutor]

    def get(self, request):
        """Получение списка файлов, загруженных учителем."""
        user = self.request.user
        profile = user.userprofile
        files = profile.files.all()
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Загрузка нового файла учителем."""
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            profile = user.userprofile
            serializer.save(tutor=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, file_id):
        """Удаление файла по id."""
        user = self.request.user
        profile = user.userprofile
        file = get_object_or_404(File, id=file_id, tutor=profile)
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class test_send(APIView):
    def get(self, request):
        from apps.notifications.tasks import send_notification
        id = send_notification.delay(request.user.id, 'тест').id
        return Response(data={'id': id}, status=status.HTTP_200_OK)
