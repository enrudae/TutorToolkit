import uuid
from django.db import models
from apps.education_plan.models import EducationPlan


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    education_plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
