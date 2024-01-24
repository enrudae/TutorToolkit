from django.db import models
from apps.education_plan.models import EducationPlan


class Lesson(models.Model):
    education_plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    notification_task_id = models.CharField(blank=True)
