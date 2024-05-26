import uuid
from django.db import models
from apps.education_plan.models import EducationPlan, Card


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    education_plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    is_canceled = models.BooleanField(default=False)
