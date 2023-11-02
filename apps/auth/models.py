from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    TUTOR = 'tutor'
    STUDENT = 'student'
    ROLE_CHOICES = [
        (TUTOR, 'Tutor'),
        (STUDENT, 'Student'),
    ]

    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']


class Tutor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'
