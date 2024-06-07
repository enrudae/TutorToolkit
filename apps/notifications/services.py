from datetime import timedelta
from apps.notifications.models import Notification
from apps.education_plan.services import StudentInvitationService
from apps.notifications.tasks import send_notification
import celery_app


class NotificationContentProvider:

    @staticmethod
    def get_invite_content(plan, email):
        tutor = plan.tutor
        text = f'Преподаватель {tutor.last_name} {tutor.first_name} приглашает Вас подключиться к дисциплине {plan.discipline}'
        content = plan.invite_code
        return text, content

    @staticmethod
    def get_repetition_reminder_content(card):
        text = f'Необходимо повторить тему {card.title}'
        content = card.id
        return text, content

    @staticmethod
    def get_lesson_reminder_content(plan, lesson):
        text = f'Урок по предмету {plan.discipline} будет через 3 часа'
        return text, ''

    @staticmethod
    def get_rescheduling_content(plan, lesson):
        text = f'Урок по предмету {plan.discipline} перенесен на {lesson.date_start.strftime("%d.%m %H:%M")}'
        return text, ''

    @staticmethod
    def get_canceling_content(plan, lesson):
        text = f'Урок по предмету {plan.discipline} {lesson.date_start.strftime("%d.%m %H:%M")} отменен'
        return text, ''


class NotificationService:

    @staticmethod
    def create_notification(plan, notification_type, text, content, lesson=None):
        is_active = notification_type not in ('lesson_reminder', 'repetition_reminder')

        notification = Notification(
            text=text,
            content=content,
            type=notification_type,
            education_plan=plan,
            lesson=lesson,
            recipient=plan.student,
            is_active=is_active
        )
        notification.save()

        NotificationService.schedule_notification(notification, plan.student.id, lesson)

        return notification

    @staticmethod
    def schedule_notification(notification, student_id, lesson=None):
        task_id = f"notification-{notification.id}"

        if notification.type == 'lesson_reminder' and lesson:
            notification_time = lesson.date_start - timedelta(hours=3)
            send_notification.apply_async((student_id, notification.text, lesson.id), eta=notification_time, task_id=task_id)
        else:
            send_notification.apply_async((student_id, notification.text, lesson.id if lesson else None), task_id=task_id)

    @staticmethod
    def cancel_lesson_reminder_notification(lesson):
        notification_for_cancelled = Notification.objects.filter(lesson=lesson, type='lesson_reminder').first()
        if notification_for_cancelled:
            res = celery_app.delete_task(f"notification-{notification_for_cancelled.id}")
            print(res)


    @staticmethod
    def handle_invite(plan, email):
        text, content = NotificationContentProvider.get_invite_content(plan, email)
        NotificationService.create_notification(plan, 'invite', text, content)

    @staticmethod
    def handle_lesson_reminder(plan, lesson):
        text, content = NotificationContentProvider.get_lesson_reminder_content(plan, lesson)
        NotificationService.create_notification(plan, 'lesson_reminder', text, content, lesson)

    @staticmethod
    def handle_repetition_reminder(plan, card):
        text, content = NotificationContentProvider.get_repetition_reminder_content(card)
        NotificationService.create_notification(plan, 'repetition_reminder', text, content)

    @staticmethod
    def handle_canceling(plan, lesson):
        NotificationService.cancel_lesson_reminder_notification(lesson)
        text, content = NotificationContentProvider.get_canceling_content(plan, lesson)
        NotificationService.create_notification(plan, 'canceling', text, content, lesson)

    @staticmethod
    def handle_rescheduling(plan, lesson):
        NotificationService.handle_canceling(plan, lesson)
        NotificationService.handle_lesson_reminder(plan, lesson)
