from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.education_plan.models import EducationPlan, PendingStudent
from apps.education_plan.serializers import EducationPlanSerializer, PendingStudentSerializer
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

    @action(methods=['post'], detail=True)
    def add_pending_student(self, request, pk=None):
        plan = self.get_object()
        print(1111, plan)

        if plan.pending_student:
            return Response({'detail': 'В этот план уже добавлен студент'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PendingStudentSerializer(data=request.data)

        if serializer.is_valid():
            student = serializer.save()
            plan.pending_student = student
            plan.save()
            return Response({'detail': 'Студент добавлен к учебному плану'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

