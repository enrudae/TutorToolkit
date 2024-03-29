import random
import string
import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from apps.account.models import UserProfile


class EducationPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tutor = models.ForeignKey(UserProfile, related_name='tutor_plans', on_delete=models.CASCADE)
    student = models.ForeignKey(UserProfile, related_name='student_plans', on_delete=models.CASCADE, blank=True, null=True)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=25)
    tutor = models.ForeignKey(UserProfile, related_name='labels', on_delete=models.CASCADE)
    color = models.CharField(
        max_length=7,
        default='#FF1493',
        validators=[
            RegexValidator(regex='^#[0-9A-Fa-f]{6}$',
                           message='Hex color must be a valid code starting with a hashtag and exactly 6 characters.'),
        ],
    )

    class Meta:
        verbose_name = "Метка"
        verbose_name_plural = "Метки"
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'tutor'],
                name='unique_label_title_tutor'
            )
        ]

    def __str__(self):
        return self.title


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=25)
    plan = models.ForeignKey(EducationPlan, related_name='modules', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=25)
    description = models.CharField(max_length=255, blank=True)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    plan_time = models.DurationField(blank=True, null=True)
    result_time = models.DurationField(blank=True, null=True)
    module = models.ForeignKey(Module, related_name='cards', on_delete=models.CASCADE)
    labels = models.ManyToManyField(Label, related_name='cards', blank=True)
    index = models.IntegerField()

    STATUS_CHOICES = (
        ('not_started', 'NOT_STARTED'),
        ('in_progress', 'IN_PROGRESS'),
        ('done', 'DONE'),
        ('to_repeat', 'TO_REPEAT'),
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')

    DIFFICULTY_CHOICES = (
        ('not_selected', 'NOT_SELECTED'),
        ('easy', 'EASY'),
        ('medium', 'MEDIUM'),
        ('hard', 'HARD'),
    )
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='not_selected')

    def save(self, *args, **kwargs):
        # Если поле index не установлено, установите его
        if not self.index:
            self.index = self.module.cards.count()
        super().save(*args, **kwargs)

    # def perform_create(self, serializer):
    #     instance = serializer.save()
    #     instance.index = instance.module.cards.count()
    #     instance.save()

    def __str__(self):
        return self.title
