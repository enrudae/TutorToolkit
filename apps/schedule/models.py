from django.db import models
from apps.education_plan.models import EducationPlan


class Lesson(models.Model):
    education_plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)
