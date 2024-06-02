import random
import string
import uuid
from django.db import models
from django.core.validators import RegexValidator
from apps.account.models import UserProfile
from apps.education_plan.tasks import change_card_status_to_repeat
from TutorToolkit.constants import FILE_RESTRICTIONS


class EducationPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tutor = models.ForeignKey(UserProfile, related_name='tutor_plans', on_delete=models.CASCADE)
    student = models.ForeignKey(UserProfile, related_name='student_plans', on_delete=models.CASCADE, blank=True, null=True)
    invite_code = models.CharField(max_length=8, unique=True, db_index=True)
    discipline = models.CharField(max_length=100, blank=True)
    student_first_name = models.CharField(max_length=50)
    student_last_name = models.CharField(max_length=50)
    student_email = models.CharField(max_length=50)

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
    title = models.CharField(max_length=100)
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
    title = models.CharField(max_length=100)
    plan = models.ForeignKey(EducationPlan, related_name='modules', on_delete=models.CASCADE)
    index = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.index is None:
            self.index = self.plan.modules.count()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    plan_time = models.DurationField(blank=True, null=True)
    result_time = models.DurationField(blank=True, null=True)
    repetition_date = models.DateTimeField(blank=True, null=True)
    module = models.ForeignKey(Module, related_name='cards', on_delete=models.CASCADE, blank=True, null=True)
    labels = models.ManyToManyField(Label, related_name='cards', blank=True)
    index = models.IntegerField(blank=True, null=True)
    is_template = models.BooleanField(default=False)

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

    def handle_repetition_task(self):
        task_id = f"change_status-{self.id}"

        # status = celery_app.delete_task(task_id)

        if self.repetition_date:
            change_card_status_to_repeat.apply_async((self.id,), eta=self.repetition_date, task_id=task_id)

    def save(self, *args, **kwargs):
        if self.index is None and not self.is_template:
            self.index = self.module.cards.count()
        super().save(*args, **kwargs)
        self.handle_repetition_task()

    def create_template(self):
        template = Card.objects.create(
            title=self.title,
            description=self.description,
            is_template=True
        )
        template.labels.set(self.labels.all())

        card_content = self.content

        CardContent.objects.create(
            card=template,
            homework=self._copy_section_content(card_content.homework),
            lesson=self._copy_section_content(card_content.lesson),
            repetition=self._copy_section_content(card_content.repetition)
        )
        return template

    def create_card_from_template(self, module):
        if not self.is_template:
            raise ValueError("Only templates can be used to create new cards.")

        card = Card.objects.create(
            title=self.title,
            description=self.description,
            module=module
        )
        card.labels.set(self.labels.all())

        card_content = self.content
        new_homework = self._copy_section_content(card_content.homework)
        new_lesson = self._copy_section_content(card_content.lesson)
        new_repetition = self._copy_section_content(card_content.repetition)

        CardContent.objects.create(
            card=card,
            homework=new_homework,
            lesson=new_lesson,
            repetition=new_repetition
        )
        return card

    @staticmethod
    def _copy_section_content(section_content):
        if section_content is None:
            return None
        new_section_content = SectionContent.objects.create(text=section_content.text)
        new_section_content.files.set(section_content.files.all())
        return new_section_content

    def __str__(self):
        return self.title


class File(models.Model):
    FILE_TYPE_CHOICES = [(ext, data['display']) for ext, data in FILE_RESTRICTIONS.items()]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    upload_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, editable=False)
    extension = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, editable=False)
    size = models.PositiveBigIntegerField(default=0, editable=False)
    tutor = models.ForeignKey(UserProfile, related_name='files', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.file.name} ({self.extension}, {self.size} bytes)"


class SectionContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(blank=True)
    files = models.ManyToManyField(File, related_name='section_contents', blank=True)

    def __str__(self):
        return f"{self.id}"


class CardContent(models.Model):
    card = models.OneToOneField(Card, primary_key=True, related_name='content', on_delete=models.CASCADE)
    homework = models.OneToOneField(SectionContent, related_name='homework', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    lesson = models.OneToOneField(SectionContent, related_name='lesson', on_delete=models.SET_NULL, null=True,
                                  blank=True)
    repetition = models.OneToOneField(SectionContent, related_name='repetition', on_delete=models.SET_NULL, null=True,
                                      blank=True)
