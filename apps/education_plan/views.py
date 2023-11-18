from django.db.models import Q
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from apps.education_plan.models import Invitations, Module
from apps.education_plan.serializers import InvitationsSerializer, ModuleSerializer
from TutorToolkit.permissions import IsTutor, IsTutorCreator


class InvitationsViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = InvitationsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Invitations.objects.filter(
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
        invitation_id = self.kwargs.get('invitation_id')
        invitation = Invitations.objects.filter(
            Q(id=invitation_id) &
            Q(tutor=user.tutor) if user.role == 'tutor' else Q(student=user.student)
        ).first()

        if not invitation:
            raise Http404('Учебного плана с таким id не найдено')

        modules = invitation.module_set.all()
        return modules


class AddStudentToInvitations(APIView):
    def post(self, request, invite_code):
        if request.user.role != 'student':
            return Response({'detail': 'Приглашением может воспользоваться только студент.'},
                            status=status.HTTP_403_FORBIDDEN)

        invite = Invitations.objects.filter(invite_code=invite_code).first()
        if not invite:
            return Response({'detail': 'Приглашение с данным кодом не найдено.'}, status=status.HTTP_404_NOT_FOUND)

        if invite.student == request.user.student:
            return Response({'detail': 'Вы уже добавлены к этому учителю.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if invite.student:
            return Response({'detail': 'Приглашение использовано другим студентом.'},
                            status=status.HTTP_400_BAD_REQUEST)

        student = request.user.student

        invite.student = student
        invite.status = 'active'
        invite.save()

        return Response({'detail': 'Студент добавлен к учителю.'}, status=status.HTTP_200_OK)
