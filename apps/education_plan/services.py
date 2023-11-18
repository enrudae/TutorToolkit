from rest_framework import status


class StudentInvitationService:
    @staticmethod
    def check_available_invite_code(invite_code):
        from .models import Invitations
        invite = Invitations.objects.filter(invite_code=invite_code).first()

        if not invite:
            return None, {'detail': 'Приглашение с данным кодом не найдено.'}, status.HTTP_404_NOT_FOUND

        if invite.student:
            return None, {'detail': 'Приглашение использовано другим студентом.'}, status.HTTP_400_BAD_REQUEST

        return invite, None, None


    @staticmethod
    def add_student_to_invitation(invite_code, student):
        invite, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)

        if error_response:
            return error_response, status_code

        invite.student = student
        invite.status = 'active'
        invite.save()

        return {'detail': 'Студент добавлен к учителю.'}, status.HTTP_200_OK
