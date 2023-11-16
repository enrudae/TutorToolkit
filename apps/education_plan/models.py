import random
import string
from django.db import models
from apps.account.models import Tutor, Student


class Invitations(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    invite_code = models.CharField(max_length=8, unique=True)
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


class EducationPlan(models.Model):
    title = models.CharField(max_length=25)
    invitation = models.OneToOneField(Invitations, on_delete=models.CASCADE, blank=True, null=True)
