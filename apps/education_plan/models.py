import random
import string
from django.db import models
from apps.account.models import Tutor, Student


class EducationPlan(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    invite_code = models.CharField(max_length=8, unique=True, db_index=True)
    student_first_name = models.CharField(max_length=50)
    student_last_name = models.CharField(max_length=50)

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_unique_invite_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student_first_name} {self.student_last_name}'

    @classmethod
    def generate_unique_invite_code(cls):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not cls.objects.filter(invite_code=code).exists():
                return code

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tutor', 'student'],
                name='unique_tutor_student'
            )
        ]


class Label(models.Model):
    title = models.CharField(max_length=25)

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=25)
    plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Card(models.Model):
    title = models.CharField(max_length=25)
    description = models.CharField(max_length=255, blank=True, null=True)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    plan_time = models.DurationField(blank=True, null=True)
    result_time = models.DurationField(blank=True, null=True)
    module = models.ForeignKey(Module, related_name='cards', on_delete=models.CASCADE)
    labels = models.ManyToManyField(Label, blank=True)

    STATUS_CHOICES = (
        ('not_started', 'NOT_STARTED'),
        ('in_progress', 'IN_PROGRESS'),
        ('done', 'DONE'),
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')

    def __str__(self):
        return self.title

