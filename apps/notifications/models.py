import uuid
from django.db import models
from apps.education_plan.models import EducationPlan
from apps.account.models import UserProfile
from apps.schedule.models import Lesson


class Notification(models.Model):
    TYPE_CHOICES = (
        ('lesson_reminder', 'LESSON_REMINDER'),
        ('repetition_reminder', 'REPETITION_REMINDER'),
        ('homework_info', 'HOMEWORK_INFO'),
        ('invite', 'INVITE'),
        ('canceling', 'CANCELING'),
        ('rescheduling', 'RESCHEDULING')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=200, blank=True)
    content = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    education_plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True)
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
