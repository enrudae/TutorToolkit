import random
import string
from django.db import models
from apps.account.models import Tutor, Student


class EducationPlan(models.Model):
    title = models.CharField(max_length=25)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    invite_code = models.CharField(max_length=8, unique=True)

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    @classmethod
    def generate_unique_invite_code(cls):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not cls.objects.filter(invite_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_unique_invite_code()
        super().save(*args, **kwargs)

