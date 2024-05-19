from celery import shared_task


@shared_task
def change_card_status_to_repeat(card_id):
    from apps.education_plan.models import Card
    from apps.notifications.models import Notification
    card = Card.objects.filter(id=card_id).first()
    if card:
        card.status = 'to_repeat'
        card.save()
        Notification.create_notification(card.module.plan, 'repetition_reminder', card=card)
