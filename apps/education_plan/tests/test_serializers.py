from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.education_plan.models import Label
from apps.education_plan.serializers import LabelSerializer

User = get_user_model()


class LabelSerializerTestCase(TestCase):
    def test_label_serializer(self):
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpassword', role='tutor')
        self.tutor = self.user.userprofile
        label_1 = Label.objects.create(title='Test Label 1', color='#FF0000', tutor=self.tutor)
        label_2 = Label.objects.create(title='Test Label 2', color='#FFFFFF', tutor=self.tutor)
        serialized_data = LabelSerializer([label_1, label_2], many=True).data
        expected_data = [
            {
                'id': label_1.id,
                'title': 'Test Label 1',
                'color': '#FF0000',
            },
            {
                'id': label_2.id,
                'title': 'Test Label 2',
                'color': '#FFFFFF',
            }
        ]
        self.assertEqual(serialized_data, expected_data)
