from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.account.serializers import ProfileSerializer
from apps.education_plan.models import Label, EducationPlan, Module, Card
from apps.education_plan.serializers import LabelSerializer, EducationPlanForStudentSerializer, \
    EducationPlanForTutorSerializer

User = get_user_model()


class LabelAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpassword', role='tutor')
        self.tutor = self.user.userprofile

        self.another_user = User.objects.create_user(email='another_user2@gmail.com', password='testpassword',
                                                     role='tutor')
        self.another_tutor = self.another_user.userprofile

        self.label = Label.objects.create(title='Test Label', color='#FF0000', tutor=self.tutor)
        self.label2 = Label.objects.create(title='Test Label2', color='#FF0000', tutor=self.tutor)
        self.another_label = Label.objects.create(title='Test Label3', color='#FF0000', tutor=self.another_tutor)

    def test_create_label(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Label', 'color': '#FF0000'}
        response = self.client.post(reverse('label-list'), data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        created_label_id = response.data.get('id', None)
        self.assertIsNotNone(created_label_id)

        created_label = Label.objects.filter(id=created_label_id).first()
        serialized_data = LabelSerializer(created_label).data
        self.assertEqual(serialized_data, response.data)

    def test_list_labels(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('label-list'))
        serialized_data = LabelSerializer([self.label, self.label2], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serialized_data, response.data)

    def test_update_label(self):
        self.client.force_authenticate(user=self.user)
        label = Label.objects.create(title='Label', color='#00FF00', tutor=self.user.userprofile)

        update_data = {'title': 'Updated Label', 'color': '#1111FF'}
        response = self.client.patch(reverse('label-detail', kwargs={'pk': label.id}), update_data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        label.refresh_from_db()
        serialized_data = LabelSerializer(label).data
        self.assertEqual(serialized_data, response.data)

    def test_update_label_of_another_user(self):
        self.client.force_authenticate(user=self.user)

        other_label = Label.objects.create(title='Other User Label', color='#FF0000', tutor=self.another_tutor)

        update_data = {'title': 'Updated Other User Label', 'color': '#00FF00'}
        response = self.client.patch(reverse('label-detail', kwargs={'pk': other_label.id}), update_data)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        other_label.refresh_from_db()
        self.assertNotEqual(other_label.title, update_data['title'])
        self.assertNotEqual(other_label.color, update_data['color'])

    def test_delete_label(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('label-detail', kwargs={'pk': self.label.id}))

        with self.assertRaises(Label.DoesNotExist):
            Label.objects.get(pk=self.label.id)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_label_of_another_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('label-detail', kwargs={'pk': self.another_label.id}))

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertTrue(Label.objects.filter(pk=self.another_label.id).exists())


class GetUsersDataAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse('get_users_data')
        self.user_tutor = User.objects.create_user(email='testuser@gmail.com', password='testpassword',
                                                   role='tutor', first_name='first_name', last_name='last_name')
        self.tutor = self.user_tutor.userprofile

        self.education_plan_1 = EducationPlan.objects.create(tutor=self.tutor, discipline='Математика',
                                                             student_first_name='first_name',
                                                             student_last_name='last_name',
                                                             status='active')
        self.education_plan_2 = EducationPlan.objects.create(tutor=self.tutor, discipline='Физика',
                                                             student_first_name='first_name',
                                                             student_last_name='last_name',
                                                             status='active')

        self.user_student = User.objects.create_user(email='student@gmail.com', password='testpassword', role='student',
                                                     invite_code=self.education_plan_1.invite_code)
        self.student = self.user_student.userprofile
        self.education_plan_1.student = self.student
        self.education_plan_2.student = self.student
        self.education_plan_1.save()
        self.education_plan_2.save()

    def test_get_users_data_tutor(self):
        self.client.force_authenticate(user=self.user_tutor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tutor_serialized_data = ProfileSerializer(self.tutor).data
        plans_serialized_data = EducationPlanForTutorSerializer([self.education_plan_1, self.education_plan_2],
                                                                many=True).data

        expected_data = {
            **tutor_serialized_data,
            'plans': plans_serialized_data,
        }
        self.assertEqual(response.data, expected_data)

    def test_get_users_data_student(self):
        self.client.force_authenticate(user=self.user_student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        student_serialized_data = ProfileSerializer(self.student).data
        plans_serialized_data = EducationPlanForStudentSerializer([self.education_plan_1, self.education_plan_2],
                                                                  many=True).data

        expected_data = {
            **student_serialized_data,
            'plans': plans_serialized_data,
        }
        self.assertEqual(response.data, expected_data)


class ChangeOrderOfElementsTest(APITestCase):
    def setUp(self):
        self.user_tutor = User.objects.create_user(email='testuser@gmail.com', password='testpassword',
                                                   role='tutor', first_name='first_name', last_name='last_name')
        self.tutor = self.user_tutor.userprofile
        self.client.force_authenticate(user=self.user_tutor)

        self.plan = EducationPlan.objects.create(tutor=self.user_tutor.userprofile, student_first_name="John", student_last_name="Doe")

        self.module1 = Module.objects.create(title="Test Module1", plan=self.plan)
        self.module2 = Module.objects.create(title="Test Module2", plan=self.plan)
        self.module3 = Module.objects.create(title="Test Module3", plan=self.plan)

        self.card1 = Card.objects.create(title="Test Card1", module=self.module1)
        self.card2 = Card.objects.create(title="Test Card2", module=self.module1)
        self.card3 = Card.objects.create(title="Test Card3", module=self.module2)
        self.card4 = Card.objects.create(title="Test Card4", module=self.module2)
        self.card5 = Card.objects.create(title="Test Card5", module=self.module2)
        self.card6 = Card.objects.create(title="Test Card6", module=self.module2)

    def test_move_card_to_beginning_in_same_module(self):
        # Перемещение карточки в начало модуля и проверка индексов других карточек
        data = {
            'element_type': 'task',
            'element_id': self.card4.id,
            'destination_id': self.module2.id,
            'destination_index': 0
        }
        response = self.client.post(reverse('move_element'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card3.refresh_from_db()
        self.card4.refresh_from_db()
        self.card5.refresh_from_db()
        self.card6.refresh_from_db()
        self.assertEqual(self.card4.index, 0)
        self.assertEqual(self.card3.index, 1)
        self.assertEqual(self.card5.index, 2)
        self.assertEqual(self.card6.index, 3)

    def test_move_card_to_middle_in_same_module(self):
        # Перемещение карточки в середину модуля и проверка индексов других карточек
        data = {
            'element_type': 'task',
            'element_id': self.card1.id,
            'destination_id': self.module1.id,
            'destination_index': 1
        }
        response = self.client.post(reverse('move_element'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card1.refresh_from_db()
        self.card2.refresh_from_db()
        self.assertEqual(self.card2.index, 0)
        self.assertEqual(self.card1.index, 1)

    def test_move_card_to_empty_module(self):
        # Перемещение карточки в пустой модуль и проверка индекса
        self.assertTrue(self.module3.cards.count() == 0)
        data = {
            'element_type': 'task',
            'element_id': self.card1.id,
            'destination_id': self.module3.id,
            'destination_index': 0
        }
        response = self.client.post(reverse('move_element'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card1.refresh_from_db()
        self.card2.refresh_from_db()
        self.assertEqual(self.card1.module, self.module3)
        self.assertEqual(self.card1.index, 0)
        self.assertEqual(self.card2.index, 0)

    def test_move_card_to_different_module_non_empty(self):
        # Перемещение карточки в непустой другой модуль и проверка индексов
        data = {
            'element_type': 'task',
            'element_id': self.card2.id,
            'destination_id': self.module2.id,
            'destination_index': 1
        }
        response = self.client.post(reverse('move_element'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card2.refresh_from_db()
        self.card3.refresh_from_db()
        self.card4.refresh_from_db()
        self.card5.refresh_from_db()
        self.card6.refresh_from_db()
        self.assertEqual(self.card2.module, self.module2)
        self.assertEqual(self.card3.index, 0)
        self.assertEqual(self.card2.index, 1)
        self.assertEqual(self.card4.index, 2)
        self.assertEqual(self.card5.index, 3)
        self.assertEqual(self.card6.index, 4)

    def test_move_module_to_beginning(self):
        # Перемещение модуля в начало
        data = {
            'element_type': 'board',
            'element_id': self.module3.id,
            'destination_index': 0
        }
        response = self.client.post(reverse('move_element'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.module1.refresh_from_db()
        self.module2.refresh_from_db()
        self.module3.refresh_from_db()
        self.assertEqual(self.module3.index, 0)
        self.assertEqual(self.module1.index, 1)
        self.assertEqual(self.module2.index, 2)

    def test_move_module_to_middle(self):
        # Перемещение модуля в середину
        data = {
            'element_type': 'board',
            'element_id': self.module1.id,
            'destination_index': 1
        }
        response = self.client.post(reverse('move_element'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.module1.refresh_from_db()
        self.module2.refresh_from_db()
        self.module3.refresh_from_db()
        self.assertEqual(self.module2.index, 0)
        self.assertEqual(self.module1.index, 1)
        self.assertEqual(self.module3.index, 2)

    def test_move_module_to_end(self):
        # Перемещение модуля в конец
        data = {
            'element_type': 'board',
            'element_id': self.module1.id,
            'destination_index': 2
        }
        response = self.client.post(reverse('move_element'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.module1.refresh_from_db()
        self.module2.refresh_from_db()
        self.module3.refresh_from_db()
        self.assertEqual(self.module2.index, 0)
        self.assertEqual(self.module3.index, 1)
        self.assertEqual(self.module1.index, 2)

    def test_move_module_to_same_position(self):
        # Перемещение модуля в ту же позицию
        data = {
            'element_type': 'board',
            'element_id': self.module2.id,
            'destination_index': 1
        }
        response = self.client.post(reverse('move_element'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.module2.refresh_from_db()
        self.assertEqual(self.module2.index, 1)
