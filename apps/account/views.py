from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from djoser import signals
from drf_yasg.utils import swagger_auto_schema
from apps.account.models import UserProfile


class CustomUserViewSet(UserViewSet):
    @swagger_auto_schema(responses={201: 'User created successfully'})
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, *args, **kwargs):
        role = serializer.validated_data.get('role', '')

        if role == 'student':
            user = serializer.save(*args, **kwargs)
            signals.user_registered.send(sender=self.__class__, user=user, request=self.request)
            user.is_active = True
            user.save()
        else:
            super().perform_create(serializer, *args, **kwargs)


class SetTelegramID(APIView):
    def post(self, request, *args, **kwargs):
        from apps.education_plan.models import EducationPlan
        code = request.data.get('code')
        telegram_id = request.data.get('telegram_id')

        try:
            plan = EducationPlan.objects.get(invite_code=code)
            student = plan.student

            if student.telegram_id:
                return Response({'message': 'Профиль уже привязан к телеграм аккаунту'},
                                status=status.HTTP_403_FORBIDDEN)

            if UserProfile.objects.filter(telegram_id=telegram_id).exists():
                return Response({'message': 'Этот телеграм аккаунт уже привязан к профилю'},
                                status=status.HTTP_403_FORBIDDEN)

            student.telegram_id = telegram_id
            student.save()

            return Response({'message': 'Telegram ID успешно сохранен'}, status=status.HTTP_200_OK)

        except EducationPlan.DoesNotExist:
            return Response({'message': 'Профиль с указанным кодом не найден'}, status=status.HTTP_404_NOT_FOUND)
