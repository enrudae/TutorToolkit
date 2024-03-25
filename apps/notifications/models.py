import uuid
from django.db import models
from apps.education_plan.models import EducationPlan
from apps.account.models import UserProfile
from apps.education_plan.services import StudentInvitationService


class Notification(models.Model):
    TYPE_CHOICES = (
        ('info', 'INFO'),
        ('invite', 'INVITE'),
        ('important', 'IMPORTANT'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=200, blank=True)
    content = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notification_task_id = models.CharField(blank=True)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='not_started')
    education_plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    @staticmethod
    def create_invite_notification(plan, email):
        tutor = plan.tutor
        student = StudentInvitationService.get_user_by_email(email)
        text = f'Преподаватель {tutor.last_name} {tutor.first_name} приглашает Вас подключиться к дисциплине {plan.discipline}'
        invite_notification = Notification(
            text=text,
            content=plan.invite_code,
            type='invite',
            education_plan=plan,
            recipient=student.userprofile
        )
        invite_notification.save()
        return invite_notification
