import random
import string
from django.db import models
from django.core.validators import RegexValidator
from apps.account.models import Tutor, Student


class EducationPlan(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    invite_code = models.CharField(max_length=8, unique=True, db_index=True)
    discipline = models.CharField(max_length=80, blank=True)
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


class Label(models.Model):
    title = models.CharField(max_length=25)
    tutor = models.ForeignKey(Tutor, related_name='labels', on_delete=models.CASCADE)
    color = models.CharField(
        max_length=7,
        default='#FFFFFF',
        validators=[
            RegexValidator(regex='^#[0-9A-Fa-f]{6}$',
                           message='Hex color must be a valid code starting with a hashtag and exactly 6 characters.'),
        ],
    )

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=25)
    plan = models.ForeignKey(EducationPlan, related_name='modules', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Card(models.Model):
    title = models.CharField(max_length=25)
    description = models.CharField(max_length=255, blank=True)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    plan_time = models.DurationField(blank=True, null=True)
    result_time = models.DurationField(blank=True, null=True)
    module = models.ForeignKey(Module, related_name='cards', on_delete=models.CASCADE)
    labels = models.ManyToManyField(Label, related_name='cards', blank=True)

    STATUS_CHOICES = (
        ('not_started', 'NOT_STARTED'),
        ('in_progress', 'IN_PROGRESS'),
        ('done', 'DONE'),
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')

    def __str__(self):
        return self.title
