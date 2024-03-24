import uuid
from django.db import models
from apps.education_plan.models import EducationPlan
# from apps.account.models import


class Notification(models.Model):
    TYPE_CHOICES = (
        ('info', 'INFO'),
        ('invite', 'INVITE'),
        ('important', 'IMPORTANT'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_created=True)
    is_active = models.BooleanField(default=True)
    notification_task_id = models.CharField(blank=True)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='not_started')
    education_plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)
    # recipient = models.ForeignKey(, on_delete=models.CASCADE)
