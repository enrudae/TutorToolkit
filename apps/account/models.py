from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from apps.education_plan.services import StudentInvitationService


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email, password and role."""
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def _create_tutor(self, email, password, first_name, last_name, **extra_fields):
        user = self._create_user(email, password, **extra_fields)
        Tutor.objects.create(user=user, first_name=first_name, last_name=last_name)
        return user

    def _create_student(self, email, password, invite_code, **extra_fields):
        invite, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)

        if not invite:
            raise ValidationError(error_response)

        user = self._create_user(email, password, **extra_fields)
        student = Student.objects.create(user=user, first_name=invite.student_first_name,
                                         last_name=invite.student_last_name)

        StudentInvitationService.add_student_to_education_plan(invite_code, student)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email, password and role profile."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        role = extra_fields.get('role', '')
        invite_code = extra_fields.pop('invite_code', '')
        first_name = extra_fields.pop('first_name', '')
        last_name = extra_fields.pop('last_name', '')

        if role == 'tutor':
            return self._create_tutor(email, password, first_name, last_name, **extra_fields)
        return self._create_student(email, password, invite_code, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    TUTOR = 'tutor'
    STUDENT = 'student'
    ROLE_CHOICES = [
        (TUTOR, 'Tutor'),
        (STUDENT, 'Student'),
    ]

    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    telegram_id = models.IntegerField(blank=True, null=True)
    device_id = models.CharField(blank=True)
    receive_email_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    telegram_id = models.IntegerField(blank=True, null=True)
    device_id = models.CharField(blank=True)
    receive_email_notifications = models.BooleanField(default=True)

    # indexes = [
    #     models.Index(fields=['device_id'], unique=True, condition=models.Q(device_id__isnull=False)),
    # ]

    def __str__(self):
        return f'{self.last_name} {self.first_name}'
