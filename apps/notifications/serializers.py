from rest_framework import serializers
from apps.notifications.models import Notification
from apps.schedule.serializers import LessonSerializerForStudentSerializer
from apps.education_plan.serializers import EducationPlanForStudentSerializer

class NotificationSerializer(serializers.ModelSerializer):
    lesson = LessonSerializerForStudentSerializer(read_only=True)
    education_plan = EducationPlanForStudentSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'text', 'content', 'date', 'is_active', 'type', 'education_plan', 'lesson')
        # read_only_fields = '__all__'
