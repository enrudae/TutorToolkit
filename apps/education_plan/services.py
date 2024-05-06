from rest_framework import status
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth import get_user_model


class StudentInvitationService:
    @staticmethod
    def check_available_invite_code(invite_code):
        from .models import EducationPlan
        plan = EducationPlan.objects.filter(invite_code=invite_code).first()

        if not plan:
            return None, {'detail': 'Приглашение с данным кодом не найдено.'}, status.HTTP_404_NOT_FOUND

        if plan.student:
            return None, {'detail': 'Приглашение использовано другим студентом.'}, status.HTTP_403_FORBIDDEN

        return plan, None, None

    @staticmethod
    def add_student_to_education_plan(invite_code, student):
        plan, error_response, status_code = StudentInvitationService.check_available_invite_code(invite_code)

        if error_response:
            return error_response, status_code

        plan.student = student
        plan.status = 'active'
        plan.save()

        return {'detail': 'Студент добавлен к учителю.'}, status.HTTP_200_OK

    @staticmethod
    def check_email_exists(email):
        User = get_user_model()
        return User.objects.filter(email=email).exists()

    @staticmethod
    def get_user_by_email(email):
        User = get_user_model()
        return get_object_or_404(User, email=email)

    @staticmethod
    def get_userprofile_by_email(email):
        user = StudentInvitationService.get_user_by_email(email)
        return user.userprofile


class MoveElementService:
    """Перемещение карточки."""
    @staticmethod
    def move_card(card, destination_index, destination_module):
        source_module = card.module
        source_index = card.index

        with transaction.atomic():
            if source_module != destination_module:
                MoveElementService.update_indexes_for_move_card_in_different_modules(source_module, source_index, destination_module, destination_index)
            else:
                MoveElementService.update_indexes_for_move_in_same_element(source_module.cards.all(), source_index, destination_index)

            card.index = destination_index
            card.module = destination_module
            card.save()

    @staticmethod
    def move_module(module, destination_index):
        """Перемещение модуля."""
        with transaction.atomic():
            source_index = module.index
            plan = module.plan
            MoveElementService.update_indexes_for_move_in_same_element(plan.modules.all(), source_index, destination_index)
            module.index = destination_index
            module.save()

    @staticmethod
    def update_indexes_for_move_card_in_different_modules(source_module, source_index, destination_module, destination_index):
        """Обновление индексов карточек при перемещении между модулями."""
        source_module.cards.filter(index__gt=source_index).update(index=F('index') - 1)
        destination_module.cards.filter(index__gte=destination_index).update(index=F('index') + 1)

    @staticmethod
    def update_indexes_for_move_in_same_element(queryset, source_index, destination_index):
        """Обновление индексов элементов при перемещении в одном наборе."""
        if source_index > destination_index:
            queryset.filter(index__gte=destination_index, index__lt=source_index).update(index=F('index') + 1)
        elif source_index < destination_index:
            queryset.filter(index__gt=source_index, index__lte=destination_index).update(index=F('index') - 1)
