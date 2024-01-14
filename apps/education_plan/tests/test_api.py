from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.account.serializers import ProfileSerializer
from apps.education_plan.models import Label, EducationPlan
from apps.education_plan.serializers import LabelSerializer, EducationPlanForStudentSerializer

User = get_user_model()


class LabelAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpassword', role='tutor')
        self.tutor = self.user.tutor

        self.another_user = User.objects.create_user(email='another_user2@gmail.com', password='testpassword',
                                                     role='tutor')
        self.another_tutor = self.another_user.tutor

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
        label = Label.objects.create(title='Label', color='#00FF00', tutor=self.user.tutor)

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
        self.tutor = self.user_tutor.tutor

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
        self.student = self.user_student.student
        self.education_plan_1.student = self.student
        self.education_plan_2.student = self.student
        self.education_plan_1.save()
        self.education_plan_2.save()

    def test_get_users_data_tutor(self):
        self.client.force_authenticate(user=self.user_tutor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tutor_serialized_data = ProfileSerializer(self.tutor).data
        plans_serialized_data = EducationPlanForStudentSerializer([self.education_plan_1, self.education_plan_2],
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
