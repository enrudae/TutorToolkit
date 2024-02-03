from rest_framework import status
from django.contrib.auth import get_user_model


class StudentInvitationService:
    @staticmethod
    def check_available_invite_code(invite_code):
        from .models import EducationPlan
        plan = EducationPlan.objects.filter(invite_code=invite_code).first()

        if not plan:
            return None, {'detail': 'Приглашение с данным кодом не найдено.'}, status.HTTP_404_NOT_FOUND

        if plan.student:
            return None, {'detail': 'Приглашение использовано другим студентом.'}, status.HTTP_403_FORBIDDEN

        return plan, None, None

    @staticmethod
    def add_student_to_education_plan(invite_code, student):
        plan, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)

        if error_response:
            return error_response, status_code

        plan.student = student
        plan.status = 'active'
        plan.save()

        return {'detail': 'Студент добавлен к учителю.'}, status.HTTP_200_OK

    @staticmethod
    def check_email_exists(email):
        User = get_user_model()
        return User.objects.filter(email=email).exists()
